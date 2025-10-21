"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface CaptchaDisplayProps {
  onVerified: () => void
}

export default function CaptchaDisplay({ onVerified }: CaptchaDisplayProps) {
  const [isVerified, setIsVerified] = useState(false)
  const [captchaCode, setCaptchaCode] = useState("")
  const [sessionId, setSessionId] = useState("")
  const [userInput, setUserInput] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    fetchCaptcha()
  }, [])

  const fetchCaptcha = async () => {
    try {
      setIsLoading(true)
      setError("")
      const response = await fetch("/api/captcha")
      const data = await response.json()
      setCaptchaCode(data.captchaCode)
      setSessionId(data.sessionId)
      setUserInput("")
    } catch (err) {
      setError("Failed to load captcha. Please try again.")
      console.error("Captcha fetch error:", err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleVerify = () => {
    if (userInput.toUpperCase() === captchaCode) {
      setIsVerified(true)
      onVerified()
    } else {
      setError("Incorrect captcha. Please try again.")
      setUserInput("")
      fetchCaptcha()
    }
  }

  if (isVerified) {
    return (
      <div className="rounded-md bg-green-50 p-4 text-green-700">
        <p className="text-sm font-medium">Captcha verified successfully</p>
      </div>
    )
  }

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Captcha Display */}
        <div className="flex items-center gap-4">
          <div className="flex-1 rounded-md border-2 border-dashed border-border bg-muted p-4 text-center font-mono text-2xl font-bold text-foreground tracking-widest min-h-16 flex items-center justify-center">
            {isLoading ? "Loading..." : captchaCode}
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={fetchCaptcha}
            disabled={isLoading}
            className="text-xs bg-transparent"
          >
            Refresh
          </Button>
        </div>

        {/* Error Message */}
        {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}

        {/* Input */}
        <div>
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value.toUpperCase())}
            placeholder="Enter the code above"
            disabled={isLoading}
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
          />
        </div>

        {/* Verify Button */}
        <Button
          type="button"
          onClick={handleVerify}
          disabled={isLoading || !userInput}
          className="w-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          Verify
        </Button>
      </div>
    </Card>
  )
}
