export async function GET() {
  const courts = [
    { id: "delhi", name: "Delhi High Court", state: "Delhi" },
    { id: "bombay", name: "Bombay High Court", state: "Maharashtra" },
    { id: "madras", name: "Madras High Court", state: "Tamil Nadu" },
    { id: "calcutta", name: "Calcutta High Court", state: "West Bengal" },
    { id: "punjab", name: "Punjab High Court", state: "Punjab" },
    { id: "allahabad", name: "Allahabad High Court", state: "Uttar Pradesh" },
    { id: "hyderabad", name: "Hyderabad High Court", state: "Telangana" },
    { id: "kerala", name: "Kerala High Court", state: "Kerala" },
    { id: "karnataka", name: "Karnataka High Court", state: "Karnataka" },
    { id: "rajasthan", name: "Rajasthan High Court", state: "Rajasthan" },
  ]

  return Response.json({ courts })
}
