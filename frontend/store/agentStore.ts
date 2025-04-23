import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Define types
export interface ClientData {
  full_name?: string;
  email?: string;
  phone?: string;
  preferred_contact?: string;
  transaction_type?: string;
  timeline?: string;
  budget?: string;
  location?: string;
  bedrooms?: string;
  property_type?: string;
  must_haves?: string;
  pre_approval?: boolean;
  payment_method?: string;
  pets?: string;
  accessibility?: string;
  urgency?: string;
  additional_notes?: string;
  [key: string]: any;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface AgentState {
  // Mode state
  mode: 'text' | 'voice';
  isTransitioning: boolean;
  
  // Client data
  clientData: ClientData;
  
  // Conversation state
  conversationHistory: Message[];
  currentStage: string;
  sessionId: string;
  
  // Connection details for voice mode
  connectionDetails: {
    url: string;
    token: string;
  } | null;
  
  // Functions
  switchMode: (newMode: 'text' | 'voice') => Promise<void>;
  updateClientData: (data: Partial<ClientData>) => void;
  addMessage: (message: Message) => void;
  sendTextMessage: (message: string) => Promise<void>;
  initialize: () => Promise<void>;
  reset: () => void;
}

export const useAgentStore = create<AgentState>()(
  devtools(
    (set, get) => ({
      // Initial state
      mode: 'text',
      isTransitioning: false,
      clientData: {},
      conversationHistory: [],
      currentStage: 'greeting',
      sessionId: `session_${Date.now()}`,
      connectionDetails: null,
      
      // Functions
      switchMode: async (newMode) => {
        set({ isTransitioning: true });
        
        try {
          // Call API to switch mode
          const response = await fetch('/api/intake/switch-mode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: get().sessionId,
              current_mode: get().mode,
              new_mode: newMode,
              agent_state: {
                client_data: get().clientData,
                conversation_history: get().conversationHistory.map(msg => ({
                  role: msg.role,
                  content: msg.content
                })),
                current_stage: get().currentStage
              }
            })
          });
          
          const data = await response.json();
          
          if (newMode === 'voice') {
            // Switching to voice mode
            set({
              mode: 'voice',
              isTransitioning: false,
              connectionDetails: data.connection_details
            });
          } else {
            // Switching to text mode
            set({
              mode: 'text',
              isTransitioning: false,
              connectionDetails: null
            });
            
            // Add transition message if provided
            if (data.message) {
              get().addMessage({
                role: 'assistant',
                content: data.message,
                timestamp: Date.now()
              });
            }
            
            // Update state if provided
            if (data.state) {
              set({
                clientData: data.state.client_data || {},
                currentStage: data.state.current_stage || 'greeting'
              });
            }
          }
        } catch (error) {
          console.error('Error switching modes:', error);
          set({ isTransitioning: false });
        }
      },
      
      updateClientData: (data) => {
        set({ clientData: { ...get().clientData, ...data } });
      },
      
      addMessage: (message) => {
        set({ conversationHistory: [...get().conversationHistory, message] });
      },
      
      sendTextMessage: async (message) => {
        // Add user message to history
        const userMessage = { role: 'user', content: message, timestamp: Date.now() };
        get().addMessage(userMessage);
        
        try {
          // Send to API
          const response = await fetch('/api/intake/text-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message,
              session_id: get().sessionId,
              agent_state: {
                client_data: get().clientData,
                conversation_history: get().conversationHistory.map(msg => ({
                  role: msg.role,
                  content: msg.content
                })),
                current_stage: get().currentStage
              }
            })
          });
          
          const data = await response.json();
          
          // Add assistant response to history
          const assistantMessage = { 
            role: 'assistant', 
            content: data.response, 
            timestamp: Date.now() 
          };
          get().addMessage(assistantMessage);
          
          // Update client data with any extracted information
          if (data.client_data) {
            get().updateClientData(data.client_data);
          }
          
          // Update current stage if provided
          if (data.state && data.state.current_stage) {
            set({ currentStage: data.state.current_stage });
          }
        } catch (error) {
          console.error('Error sending message:', error);
          
          // Add error message
          get().addMessage({
            role: 'assistant',
            content: 'Sorry, I encountered an error processing your message. Please try again.',
            timestamp: Date.now()
          });
        }
      },
      
      initialize: async () => {
        try {
          // Get initial greeting
          const response = await fetch(`/api/intake/initial-greeting/${get().sessionId}`);
          const data = await response.json();
          
          // Add greeting to conversation history
          get().addMessage({
            role: 'assistant',
            content: data.greeting,
            timestamp: Date.now()
          });
          
          // Update state if provided
          if (data.state) {
            set({
              clientData: data.state.client_data || {},
              currentStage: data.state.current_stage || 'greeting'
            });
          }
        } catch (error) {
          console.error('Error initializing agent:', error);
          
          // Add fallback greeting
          get().addMessage({
            role: 'assistant',
            content: 'Hello! I\'m your real estate intake assistant. How can I help you today?',
            timestamp: Date.now()
          });
        }
      },
      
      reset: () => {
        set({
          mode: 'text',
          isTransitioning: false,
          clientData: {},
          conversationHistory: [],
          currentStage: 'greeting',
          sessionId: `session_${Date.now()}`,
          connectionDetails: null
        });
        
        // Initialize with greeting
        get().initialize();
      }
    })
  )
);
