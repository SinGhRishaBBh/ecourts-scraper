"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import SearchForm from "@/components/search-form"
import ResultsDisplay from "@/components/results-display"
import BulkDownloadProgress from "@/components/bulk-download-progress"

export default function Home() {
  const [searchResults, setSearchResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set())
  const [isDownloading, setIsDownloading] = useState(false)

  const handleSearch = async (formData: any) => {
    setIsLoading(true)
    try {
      // Simulate API call to fetch documents
      // In a real implementation, this would call the eCourts API
      const mockResults = [
        {
          id: "doc1",
          title: "Case Order - 2024",
          description: "High Court Order dated January 15, 2024",
        },
        {
          id: "doc2",
          title: "Judgment - 2024",
          description: "Judgment delivered on February 20, 2024",
        },
        {
          id: "doc3",
          title: "Petition - 2024",
          description: "Original Petition filed on March 10, 2024",
        },
      ]
      setSearchResults(mockResults)
      setSelectedItems(new Set())
    } catch (error) {
      console.error("Search error:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleBulkDownload = async () => {
    if (selectedItems.size === 0) {
      alert("Please select items to download")
      return
    }

    setIsDownloading(true)

    try {
      const selectedIds = Array.from(selectedItems).map((index) => searchResults[Number.parseInt(index)].id)

      const response = await fetch("/api/bulk-download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentIds: selectedIds }),
      })

      if (!response.ok) {
        throw new Error("Bulk download failed")
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = `ecourts-documents-${Date.now()}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setSelectedItems(new Set())
    } catch (error) {
      console.error("Bulk download error:", error)
      alert("Failed to download documents")
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-foreground">eCourts Search</h1>
              <p className="mt-1 text-sm text-muted-foreground">Search and download court documents</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Search Form */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <h2 className="mb-6 text-xl font-semibold text-foreground">Search Documents</h2>
              <SearchForm onSearch={handleSearch} isLoading={isLoading} />
            </Card>
          </div>

          {/* Info Sidebar */}
          <div className="space-y-4">
            <Card className="p-4">
              <h3 className="font-semibold text-foreground">How it works</h3>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="font-bold text-primary">1</span>
                  <span>Select court and case details</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold text-primary">2</span>
                  <span>Complete the captcha verification</span>
                </li>
                <li className="flex gap-2">
                  <span className="font-bold text-primary">3</span>
                  <span>View and download documents</span>
                </li>
              </ul>
            </Card>

            <Card className="p-4">
              <h3 className="font-semibold text-foreground">Features</h3>
              <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
                <li>Individual document download</li>
                <li>Bulk download support</li>
                <li>Progress tracking</li>
                <li>Multiple court access</li>
              </ul>
            </Card>
          </div>
        </div>

        {/* Results Section */}
        {searchResults.length > 0 && (
          <div className="mt-8">
            <Card className="p-6">
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-foreground">Results ({searchResults.length})</h2>
                {selectedItems.size > 0 && (
                  <Button
                    onClick={handleBulkDownload}
                    disabled={isDownloading}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  >
                    {isDownloading ? "Downloading..." : `Download Selected (${selectedItems.size})`}
                  </Button>
                )}
              </div>

              {isDownloading && (
                <BulkDownloadProgress selectedCount={selectedItems.size} onDownloadComplete={() => {}} />
              )}

              <ResultsDisplay
                results={searchResults}
                selectedItems={selectedItems}
                onSelectionChange={setSelectedItems}
              />
            </Card>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && searchResults.length === 0 && (
          <div className="mt-8 text-center">
            <Card className="p-12">
              <div className="text-muted-foreground">
                <p className="text-lg">No documents found</p>
                <p className="mt-2 text-sm">Use the search form to find court documents</p>
              </div>
            </Card>
          </div>
        )}
      </div>
    </main>
  )
}
