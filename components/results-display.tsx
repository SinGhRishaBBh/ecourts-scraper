"use client"

import { useState } from "react"
import { Checkbox } from "@/components/ui/checkbox"
import { Button } from "@/components/ui/button"

interface ResultsDisplayProps {
  results: any[]
  selectedItems: Set<string>
  onSelectionChange: (items: Set<string>) => void
}

export default function ResultsDisplay({ results, selectedItems, onSelectionChange }: ResultsDisplayProps) {
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const [downloadError, setDownloadError] = useState<string | null>(null)

  const handleSelectItem = (id: string) => {
    const newSelected = new Set(selectedItems)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    onSelectionChange(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedItems.size === results.length) {
      onSelectionChange(new Set())
    } else {
      onSelectionChange(new Set(results.map((_, i) => i.toString())))
    }
  }

  const handleDownload = async (documentId: string, fileName: string) => {
    setDownloadingId(documentId)
    setDownloadError(null)
    try {
      const response = await fetch("/api/download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentId, fileName }),
      })

      if (!response.ok) {
        throw new Error("Download failed")
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = `${fileName}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Download error:", error)
      setDownloadError("Failed to download document")
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Select All */}
      <div className="flex items-center gap-2 border-b border-border pb-4">
        <Checkbox checked={selectedItems.size === results.length && results.length > 0} onChange={handleSelectAll} />
        <span className="text-sm font-medium text-foreground">Select All ({results.length})</span>
      </div>

      {/* Error Message */}
      {downloadError && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{downloadError}</div>}

      {/* Results List */}
      <div className="space-y-3">
        {results.map((result, index) => (
          <div key={index} className="flex items-start gap-3 rounded-md border border-border p-4 hover:bg-muted/50">
            <Checkbox
              checked={selectedItems.has(index.toString())}
              onChange={() => handleSelectItem(index.toString())}
              className="mt-1"
            />
            <div className="flex-1">
              <h3 className="font-medium text-foreground">{result.title}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{result.description}</p>
              <div className="mt-3 flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs bg-transparent"
                  onClick={() => handleDownload(result.id, result.title)}
                  disabled={downloadingId === result.id}
                >
                  {downloadingId === result.id ? "Downloading..." : "Download"}
                </Button>
                <Button variant="outline" size="sm" className="text-xs bg-transparent">
                  Preview
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
