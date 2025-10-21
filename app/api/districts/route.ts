export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const state = searchParams.get("state")

  // Mock data - in production, this would fetch from eCourts
  const districtsByState: Record<string, string[]> = {
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Tirupati", "Nellore"],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun"],
    Assam: ["Guwahati", "Dibrugarh", "Silchar"],
    Bihar: ["Patna", "Gaya", "Muzaffarpur", "Darbhanga"],
    Chhattisgarh: ["Raipur", "Bilaspur", "Durg"],
    Delhi: ["New Delhi"],
    Goa: ["Panaji"],
    Gujarat: ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    Haryana: ["Faridabad", "Gurgaon", "Hisar"],
    "Himachal Pradesh": ["Shimla", "Kangra"],
    Jharkhand: ["Ranchi", "Dhanbad", "Giridih"],
    Karnataka: ["Bangalore", "Mangalore", "Belgaum", "Hubli"],
    Kerala: ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "Madhya Pradesh": ["Indore", "Bhopal", "Jabalpur", "Gwalior"],
    Maharashtra: ["Mumbai", "Pune", "Nagpur", "Aurangabad"],
    Manipur: ["Imphal"],
    Meghalaya: ["Shillong"],
    Mizoram: ["Aizawl"],
    Nagaland: ["Kohima"],
    Odisha: ["Bhubaneswar", "Cuttack", "Rourkela"],
    Punjab: ["Chandigarh", "Amritsar", "Ludhiana"],
    Rajasthan: ["Jaipur", "Jodhpur", "Udaipur", "Ajmer"],
    Sikkim: ["Gangtok"],
    "Tamil Nadu": ["Chennai", "Madurai", "Coimbatore", "Salem"],
    Telangana: ["Hyderabad", "Warangal"],
    Tripura: ["Agartala"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Allahabad"],
    Uttarakhand: ["Dehradun", "Nainital"],
    "West Bengal": ["Kolkata", "Darjeeling", "Asansol"],
  }

  const districts = districtsByState[state || ""] || []

  return Response.json({ districts })
}
