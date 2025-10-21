"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"

interface BulkDownloadProgressProps {
  selectedCount: number
  onDownloadComplete: () => void
}

export default function BulkDownloadProgress({ selectedCount, onDownloadComplete }: BulkDownloadProgressProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState("")

  const handleBulkDownload = async (selectedIds: string[]) => {
    setIsDownloading(true)
    setProgress(0)
    setStatus("Preparing download...")

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return prev
          }
          return prev + Math.random() * 30
        })
      }, 500)

      setStatus(`Downloading ${selectedCount} document(s)...`)

      const response = await fetch("/api/bulk-download", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ documentIds: selectedIds }),
      })

      clearInterval(progressInterval)

      if (!response.ok) {
        throw new Error("Bulk download failed")
      }

      setProgress(100)
      setStatus("Download complete!")

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = `ecourts-documents-${Date.now()}.zip`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      setTimeout(() => {
        setIsDownloading(false)
        setProgress(0)
        setStatus("")
        onDownloadComplete()
      }, 1500)
    } catch (error) {
      console.error("Bulk download error:", error)
      setStatus("Download failed. Please try again.")
      setIsDownloading(false)
    }
  }

  return (
    <div className="space-y-4">
      {isDownloading && (
        <Card className="p-4 bg-blue-50 border-blue-200">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">{status}</span>
              <span className="text-sm font-medium text-primary">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
