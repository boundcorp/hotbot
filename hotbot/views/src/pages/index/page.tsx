import * as React from "react";
import * as HomeController from "./_server";
import { createServerPage } from "@/components/ServerPages";
import { Button } from "@/components/ui/button";

const HomePage = createServerPage(HomeController);

const Home = () => {
  const context = HomePage.useContext();
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary">
      {/* Hero Section */}
      <section className="hero min-h-screen">
        <div className="hero-content text-center text-neutral-content">
          <div className="max-w-md">
            <h1 className="mb-5 text-5xl font-bold">Welcome to HotBot</h1>
            <p className="mb-5">
              The next-gen AI content analysis tool for topical conversations
            </p>
            <Button className="btn btn-primary" onClick={() => window.location.href = "/login"}>Get Started</Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-base-100">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              title="Farcaster Channel Support"
              description="Analyze conversations in Farcaster channels with ease"
            />
            <FeatureCard
              title="Advanced Content Tagging"
              description="Automatically tag content types including spam, promotional, and original content"
            />
            <FeatureCard
              title="User Quality Rating"
              description="Identify low-quality users to maintain high-quality discussions"
            />
          </div>
        </div>
      </section>
    </div>
  );
};

const FeatureCard: React.FC<{ title: string; description: string }> = ({ title, description }) => (
  <div className="card bg-base-200 shadow-xl">
    <div className="card-body">
      <h2 className="card-title">{title}</h2>
      <p>{description}</p>
    </div>
  </div>
);

export default HomePage.wraps(Home);
