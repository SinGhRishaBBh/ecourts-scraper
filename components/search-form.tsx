"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import CaptchaDisplay from "./captcha-display"

interface SearchFormProps {
  onSearch: (formData: any) => void
  isLoading: boolean
}

interface Court {
  id: string
  name: string
}

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [formData, setFormData] = useState({
    state: "",
    district: "",
    court: "",
    caseNumber: "",
    year: new Date().getFullYear().toString(),
    captchaVerified: false,
  })

  const [states, setStates] = useState<string[]>([])
  const [districts, setDistricts] = useState<string[]>([])
  const [courts, setCourts] = useState<Court[]>([])
  const [statesLoading, setStatesLoading] = useState(true)
  const [districtsLoading, setDistrictsLoading] = useState(false)
  const [courtsLoading, setCourtsLoading] = useState(false)

  useEffect(() => {
    const fetchStates = async () => {
      try {
        const response = await fetch("/api/states")
        const data = await response.json()
        setStates(data.states)
      } catch (error) {
        console.error("Failed to fetch states:", error)
      } finally {
        setStatesLoading(false)
      }
    }

    fetchStates()
  }, [])

  useEffect(() => {
    if (!formData.state) {
      setDistricts([])
      setCourts([])
      setFormData((prev) => ({ ...prev, district: "", court: "" }))
      return
    }

    const fetchDistricts = async () => {
      setDistrictsLoading(true)
      try {
        const response = await fetch(`/api/districts?state=${encodeURIComponent(formData.state)}`)
        const data = await response.json()
        setDistricts(data.districts)
      } catch (error) {
        console.error("Failed to fetch districts:", error)
      } finally {
        setDistrictsLoading(false)
      }
    }

    fetchDistricts()
  }, [formData.state])

  useEffect(() => {
    if (!formData.state || !formData.district) {
      setCourts([])
      setFormData((prev) => ({ ...prev, court: "" }))
      return
    }

    const fetchCourts = async () => {
      setCourtsLoading(true)
      try {
        const response = await fetch(
          `/api/courts-by-district?state=${encodeURIComponent(formData.state)}&district=${encodeURIComponent(formData.district)}`,
        )
        const data = await response.json()
        setCourts(data.courts)
      } catch (error) {
        console.error("Failed to fetch courts:", error)
      } finally {
        setCourtsLoading(false)
      }
    }

    fetchCourts()
  }, [formData.state, formData.district])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleCaptchaVerified = () => {
    setFormData((prev) => ({ ...prev, captchaVerified: true }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.captchaVerified) {
      alert("Please complete the captcha verification")
      return
    }
    onSearch(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* State Selection */}
      <div>
        <label className="block text-sm font-medium text-foreground">Select State</label>
        <select
          name="state"
          value={formData.state}
          onChange={handleInputChange}
          required
          disabled={statesLoading}
          className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
        >
          <option value="">{statesLoading ? "Loading states..." : "Choose a state..."}</option>
          {states.map((state) => (
            <option key={state} value={state}>
              {state}
            </option>
          ))}
        </select>
      </div>

      {/* District Selection */}
      <div>
        <label className="block text-sm font-medium text-foreground">Select District</label>
        <select
          name="district"
          value={formData.district}
          onChange={handleInputChange}
          required
          disabled={!formData.state || districtsLoading}
          className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
        >
          <option value="">
            {!formData.state
              ? "Select a state first"
              : districtsLoading
                ? "Loading districts..."
                : "Choose a district..."}
          </option>
          {districts.map((district) => (
            <option key={district} value={district}>
              {district}
            </option>
          ))}
        </select>
      </div>

      {/* Court Selection */}
      <div>
        <label className="block text-sm font-medium text-foreground">Select Court</label>
        <select
          name="court"
          value={formData.court}
          onChange={handleInputChange}
          required
          disabled={!formData.district || courtsLoading}
          className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
        >
          <option value="">
            {!formData.district ? "Select a district first" : courtsLoading ? "Loading courts..." : "Choose a court..."}
          </option>
          {courts.map((court) => (
            <option key={court.id} value={court.id}>
              {court.name}
            </option>
          ))}
        </select>
      </div>

      {/* Case Number */}
      <div>
        <label className="block text-sm font-medium text-foreground">Case Number</label>
        <input
          type="text"
          name="caseNumber"
          value={formData.caseNumber}
          onChange={handleInputChange}
          placeholder="Enter case number"
          required
          className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {/* Year */}
      <div>
        <label className="block text-sm font-medium text-foreground">Year</label>
        <input
          type="number"
          name="year"
          value={formData.year}
          onChange={handleInputChange}
          min="1950"
          max={new Date().getFullYear()}
          className="mt-2 w-full rounded-md border border-input bg-background px-3 py-2 text-foreground placeholder-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {/* Captcha */}
      <div>
        <label className="block text-sm font-medium text-foreground mb-3">Verification</label>
        <CaptchaDisplay onVerified={handleCaptchaVerified} />
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        disabled={isLoading || !formData.captchaVerified}
        className="w-full bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
      >
        {isLoading ? "Searching..." : "Search Documents"}
      </Button>
    </form>
  )
}
