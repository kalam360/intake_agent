import { NextRequest, NextResponse } from 'next/server';

// The base URL for the intake agent API
const INTAKE_API_BASE_URL = process.env.INTAKE_API_URL || 'http://localhost:8000/api/intake';

/**
 * API route handler for proxying requests to the intake agent API
 * This allows us to avoid CORS issues and keep the backend URL private
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    // Construct the target URL by joining the path segments
    const targetPath = params.path.join('/');
    const url = `${INTAKE_API_BASE_URL}/${targetPath}`;
    
    // Forward the request to the intake agent API
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Get the response data
    const data = await response.json();
    
    // Return the response
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error proxying GET request to intake API:', error);
    return NextResponse.json(
      { error: 'Failed to communicate with intake agent' },
      { status: 500 }
    );
  }
}

/**
 * API route handler for proxying POST requests to the intake agent API
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    // Get the request body
    const body = await request.json();
    
    // Construct the target URL by joining the path segments
    const targetPath = params.path.join('/');
    const url = `${INTAKE_API_BASE_URL}/${targetPath}`;
    
    // Forward the request to the intake agent API
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    // Get the response data
    const data = await response.json();
    
    // Return the response
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error proxying POST request to intake API:', error);
    return NextResponse.json(
      { error: 'Failed to communicate with intake agent' },
      { status: 500 }
    );
  }
}
