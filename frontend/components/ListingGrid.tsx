"use client";

import Image from "next/image";
import { Card, CardContent, CardFooter, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

interface Property {
  id: string;
  title: string;
  address: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  imageUrl: string;
  tags: string[];
}

const PLACEHOLDER_PROPERTIES: Property[] = [
  {
    id: "prop-1",
    title: "Modern Downtown Apartment",
    address: "123 Main St, Cityville, CA",
    price: 450000,
    bedrooms: 2,
    bathrooms: 2,
    sqft: 1200,
    imageUrl: "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=500&h=350&fit=crop",
    tags: ["Apartment", "Downtown", "New"]
  },
  {
    id: "prop-2",
    title: "Suburban Family Home",
    address: "456 Oak Ave, Suburbia, CA",
    price: 750000,
    bedrooms: 4,
    bathrooms: 3,
    sqft: 2400,
    imageUrl: "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=500&h=350&fit=crop",
    tags: ["House", "Family", "Garden"]
  },
  {
    id: "prop-3",
    title: "Luxury Beachfront Condo",
    address: "789 Ocean Blvd, Seaside, CA",
    price: 1250000,
    bedrooms: 3,
    bathrooms: 3.5,
    sqft: 2100,
    imageUrl: "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=500&h=350&fit=crop",
    tags: ["Condo", "Beachfront", "Luxury"]
  },
  {
    id: "prop-4",
    title: "Cozy Mountain Cabin",
    address: "101 Pine Trail, Mountain View, CA",
    price: 350000,
    bedrooms: 2,
    bathrooms: 1,
    sqft: 950,
    imageUrl: "https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=500&h=350&fit=crop",
    tags: ["Cabin", "Mountain", "Cozy"]
  },
  {
    id: "prop-5",
    title: "Historic Downtown Loft",
    address: "202 Brick Lane, Old Town, CA",
    price: 525000,
    bedrooms: 1,
    bathrooms: 1.5,
    sqft: 1100,
    imageUrl: "https://images.unsplash.com/photo-1494526585095-c41746248156?w=500&h=350&fit=crop",
    tags: ["Loft", "Historic", "Downtown"]
  },
  {
    id: "prop-6",
    title: "Modern Suburban Townhouse",
    address: "303 New Ave, Newtown, CA",
    price: 625000,
    bedrooms: 3,
    bathrooms: 2.5,
    sqft: 1800,
    imageUrl: "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=500&h=350&fit=crop",
    tags: ["Townhouse", "Modern", "Garage"]
  },
];

export default function ListingGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {PLACEHOLDER_PROPERTIES.map((property) => (
        <PropertyCard key={property.id} property={property} />
      ))}
    </div>
  );
}

function PropertyCard({ property }: { property: Property }) {
  const { title, address, price, bedrooms, bathrooms, sqft, imageUrl, tags } = property;
  
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative h-48 w-full">
        <Image
          src={imageUrl}
          alt={title}
          fill
          className="object-cover"
        />
      </div>
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            <p className="text-sm text-muted-foreground">{address}</p>
          </div>
          <p className="font-bold text-lg">${price.toLocaleString()}</p>
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="flex justify-between text-sm">
          <div><span className="font-medium">{bedrooms}</span> beds</div>
          <div><span className="font-medium">{bathrooms}</span> baths</div>
          <div><span className="font-medium">{sqft.toLocaleString()}</span> sqft</div>
        </div>
      </CardContent>
      <CardFooter className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <Badge key={tag} variant="secondary">{tag}</Badge>
        ))}
      </CardFooter>
    </Card>
  );
}
