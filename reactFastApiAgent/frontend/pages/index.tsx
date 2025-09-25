import { useState } from 'react';
import axios from 'axios';

// TypeScript interfaces for type safety and API response structure
interface CompetitorAnalysis {
  name: string;
  website: string;
  analysis: string;
}

interface AnalysisResponse {
  business_description: string;
  competitors: CompetitorAnalysis[];
  analysis: string;
}

export default function Home() {
  // State management for the application
  const [businessDescription, setBusinessDescription] = useState(''); // User's business description input
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null); // AI analysis results from backend
  const [loading, setLoading] = useState(false); // Loading state for API call
  const [error, setError] = useState(''); // Error messages to display to user

  // Main function to send business description to AI agent and get competitor analysis
  const analyzeCompetitors = async () => {
    // Validate user input before making API call
    if (!businessDescription.trim()) {
      setError('Please enter a business description');
      return;
    }

    // Reset UI state before making new API call
    setLoading(true); // Show loading spinner and disable button
    setError(''); // Clear any previous error messages
    setAnalysis(null); // Clear previous analysis results

    try {
      // Send POST request to FastAPI backend with business description
      const response = await axios.post('http://localhost:8001/analyze-competitors', {
        business_description: businessDescription,
        num_competitors: 5 // Request analysis of 5 competitors
      });

      // Store the AI analysis results in state to trigger UI re-render
      setAnalysis(response.data);
    } catch (err) {
      // Handle API errors and display user-friendly message
      setError('Failed to analyze competitors. Make sure the backend is running.');
      console.error(err);
    } finally {
      // Always hide loading state when API call completes (success or failure)
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Main application header */}
        <h1 className="text-4xl font-bold text-cyan-primary mb-8 text-center">
          Business Intelligence Agent
        </h1>

        {/* Input section - where users describe their business */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-8">
          <label className="block text-lg font-semibold mb-4 text-cyan-secondary">
            Business Description
          </label>

          {/* Textarea for business description input */}
          <textarea
            value={businessDescription}
            onChange={(e) => setBusinessDescription(e.target.value)}
            placeholder="Describe your business (e.g., 'AI-powered customer service platform for e-commerce companies')"
            className="w-full h-32 p-4 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-primary resize-none"
          />

          {/* Submit button - triggers AI analysis */}
          <button
            onClick={analyzeCompetitors}
            disabled={loading} // Disable button while API call is in progress
            className="mt-4 bg-cyan-primary hover:bg-cyan-secondary disabled:bg-gray-600 text-black font-semibold py-3 px-8 rounded-lg transition-colors duration-200"
          >
            {loading ? 'Analyzing...' : 'Analyze Competitors'} {/* Dynamic button text */}
          </button>

          {/* Error message display - only shows if there's an error */}
          {error && (
            <div className="mt-4 p-4 bg-red-900 border border-red-600 rounded-lg text-red-200">
              {error}
            </div>
          )}
        </div>

        {/* Results section - only renders when analysis data is available */}
        {analysis && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-cyan-secondary mb-4">
              Competitor Analysis Results
            </h2>

            {/* AI-generated overall analysis summary */}
            {analysis.analysis && (
              <div className="bg-dark-card border border-dark-border rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold text-cyan-primary mb-4">
                  AI Analysis Summary
                </h3>
                {/* whitespace-pre-wrap preserves line breaks from AI response */}
                <div className="text-green-400 leading-relaxed whitespace-pre-wrap">
                  {analysis.analysis}
                </div>
              </div>
            )}

            {/* Individual competitor cards */}
            <div className="grid gap-6">
              {analysis.competitors.map((competitor, index) => (
                <div key={index} className="bg-dark-card border border-dark-border rounded-lg p-6">
                  {/* Competitor header with name and website link */}
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-xl font-semibold text-cyan-primary">
                      {competitor.name}
                    </h3>
                    {/* External link to competitor website */}
                    <a
                      href={competitor.website}
                      target="_blank" // Opens in new tab
                      rel="noopener noreferrer" // Security best practice for external links
                      className="text-cyan-secondary hover:text-cyan-primary transition-colors duration-200 underline"
                    >
                      Visit Website
                    </a>
                  </div>

                  {/* AI-generated analysis for this specific competitor */}
                  <div className="text-green-400 leading-relaxed whitespace-pre-wrap">
                    {competitor.analysis}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Loading spinner - only shows while API call is in progress */}
        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-primary"></div>
          </div>
        )}
      </div>
    </div>
  );
}