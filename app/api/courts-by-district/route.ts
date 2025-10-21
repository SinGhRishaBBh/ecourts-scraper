export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const state = searchParams.get("state")
  const district = searchParams.get("district")

  const courtsByLocation: Record<string, Record<string, any[]>> = {
    "Andhra Pradesh": {
      Visakhapatnam: [
        { id: "ap-viz-1", name: "High Court of Andhra Pradesh, Visakhapatnam Bench" },
        { id: "ap-viz-2", name: "District Court, Visakhapatnam" },
      ],
      Vijayawada: [
        { id: "ap-vij-1", name: "High Court of Andhra Pradesh, Vijayawada Bench" },
        { id: "ap-vij-2", name: "District Court, Vijayawada" },
      ],
      Tirupati: [{ id: "ap-tir-1", name: "District Court, Tirupati" }],
      Nellore: [{ id: "ap-nel-1", name: "District Court, Nellore" }],
    },
    "Arunachal Pradesh": {
      Itanagar: [
        { id: "ar-ita-1", name: "High Court of Arunachal Pradesh" },
        { id: "ar-ita-2", name: "District Court, Itanagar" },
      ],
      Naharlagun: [{ id: "ar-nah-1", name: "District Court, Naharlagun" }],
    },
    Assam: {
      Guwahati: [
        { id: "as-guw-1", name: "Gauhati High Court" },
        { id: "as-guw-2", name: "District Court, Guwahati" },
      ],
      Dibrugarh: [{ id: "as-dib-1", name: "District Court, Dibrugarh" }],
      Silchar: [{ id: "as-sil-1", name: "District Court, Silchar" }],
    },
    Bihar: {
      Patna: [
        { id: "bh-pat-1", name: "Patna High Court" },
        { id: "bh-pat-2", name: "District Court, Patna" },
      ],
      Gaya: [{ id: "bh-gay-1", name: "District Court, Gaya" }],
      Muzaffarpur: [{ id: "bh-muz-1", name: "District Court, Muzaffarpur" }],
      Darbhanga: [{ id: "bh-dar-1", name: "District Court, Darbhanga" }],
    },
    Chhattisgarh: {
      Raipur: [
        { id: "cg-rai-1", name: "High Court of Chhattisgarh" },
        { id: "cg-rai-2", name: "District Court, Raipur" },
      ],
      Bilaspur: [{ id: "cg-bil-1", name: "District Court, Bilaspur" }],
      Durg: [{ id: "cg-dur-1", name: "District Court, Durg" }],
    },
    Delhi: {
      "New Delhi": [
        { id: "del-1", name: "Delhi High Court" },
        { id: "del-2", name: "District Court, Delhi" },
        { id: "del-3", name: "Tis Hazari Courts" },
        { id: "del-4", name: "Patiala House Courts" },
      ],
    },
    Goa: {
      Panaji: [
        { id: "ga-pan-1", name: "High Court of Bombay, Goa Bench" },
        { id: "ga-pan-2", name: "District Court, Goa" },
      ],
    },
    Gujarat: {
      Ahmedabad: [
        { id: "gj-ahm-1", name: "Gujarat High Court" },
        { id: "gj-ahm-2", name: "District Court, Ahmedabad" },
      ],
      Surat: [{ id: "gj-sur-1", name: "District Court, Surat" }],
      Vadodara: [{ id: "gj-vad-1", name: "District Court, Vadodara" }],
      Rajkot: [{ id: "gj-raj-1", name: "District Court, Rajkot" }],
    },
    Haryana: {
      Faridabad: [{ id: "hr-far-1", name: "District Court, Faridabad" }],
      Gurgaon: [{ id: "hr-gur-1", name: "District Court, Gurgaon" }],
      Hisar: [
        { id: "hr-his-1", name: "Punjab and Haryana High Court, Hisar Bench" },
        { id: "hr-his-2", name: "District Court, Hisar" },
      ],
    },
    "Himachal Pradesh": {
      Shimla: [
        { id: "hp-shim-1", name: "High Court of Himachal Pradesh" },
        { id: "hp-shim-2", name: "District Court, Shimla" },
      ],
      Kangra: [{ id: "hp-kan-1", name: "District Court, Kangra" }],
    },
    Jharkhand: {
      Ranchi: [
        { id: "jh-ran-1", name: "Jharkhand High Court" },
        { id: "jh-ran-2", name: "District Court, Ranchi" },
      ],
      Dhanbad: [{ id: "jh-dha-1", name: "District Court, Dhanbad" }],
      Giridih: [{ id: "jh-gir-1", name: "District Court, Giridih" }],
    },
    Karnataka: {
      Bangalore: [
        { id: "ka-ban-1", name: "Karnataka High Court" },
        { id: "ka-ban-2", name: "District Court, Bangalore" },
      ],
      Mangalore: [{ id: "ka-man-1", name: "District Court, Mangalore" }],
      Belgaum: [{ id: "ka-bel-1", name: "District Court, Belgaum" }],
      Hubli: [{ id: "ka-hub-1", name: "District Court, Hubli" }],
    },
    Kerala: {
      Kochi: [
        { id: "kl-koc-1", name: "Kerala High Court" },
        { id: "kl-koc-2", name: "District Court, Kochi" },
      ],
      Thiruvananthapuram: [{ id: "kl-thi-1", name: "District Court, Thiruvananthapuram" }],
      Kozhikode: [{ id: "kl-koz-1", name: "District Court, Kozhikode" }],
    },
    "Madhya Pradesh": {
      Indore: [{ id: "mp-ind-1", name: "District Court, Indore" }],
      Bhopal: [
        { id: "mp-bho-1", name: "High Court of Madhya Pradesh" },
        { id: "mp-bho-2", name: "District Court, Bhopal" },
      ],
      Jabalpur: [{ id: "mp-jab-1", name: "District Court, Jabalpur" }],
      Gwalior: [{ id: "mp-gwa-1", name: "District Court, Gwalior" }],
    },
    Maharashtra: {
      Mumbai: [
        { id: "mh-mum-1", name: "Bombay High Court" },
        { id: "mh-mum-2", name: "District Court, Mumbai" },
        { id: "mh-mum-3", name: "City Civil Court, Mumbai" },
      ],
      Pune: [
        { id: "mh-pun-1", name: "District Court, Pune" },
        { id: "mh-pun-2", name: "City Civil Court, Pune" },
      ],
      Nagpur: [
        { id: "mh-nag-1", name: "Nagpur Bench, Bombay High Court" },
        { id: "mh-nag-2", name: "District Court, Nagpur" },
      ],
      Aurangabad: [{ id: "mh-aur-1", name: "District Court, Aurangabad" }],
    },
    Manipur: {
      Imphal: [
        { id: "mn-imp-1", name: "High Court of Manipur" },
        { id: "mn-imp-2", name: "District Court, Imphal" },
      ],
    },
    Meghalaya: {
      Shillong: [
        { id: "mg-shi-1", name: "High Court of Meghalaya" },
        { id: "mg-shi-2", name: "District Court, Shillong" },
      ],
    },
    Mizoram: {
      Aizawl: [
        { id: "mz-aiz-1", name: "High Court of Mizoram" },
        { id: "mz-aiz-2", name: "District Court, Aizawl" },
      ],
    },
    Nagaland: {
      Kohima: [
        { id: "nl-koh-1", name: "High Court of Nagaland" },
        { id: "nl-koh-2", name: "District Court, Kohima" },
      ],
    },
    Odisha: {
      Bhubaneswar: [
        { id: "od-bhu-1", name: "Orissa High Court" },
        { id: "od-bhu-2", name: "District Court, Bhubaneswar" },
      ],
      Cuttack: [{ id: "od-cut-1", name: "District Court, Cuttack" }],
      Rourkela: [{ id: "od-rou-1", name: "District Court, Rourkela" }],
    },
    Punjab: {
      Chandigarh: [
        { id: "pb-cha-1", name: "Punjab and Haryana High Court" },
        { id: "pb-cha-2", name: "District Court, Chandigarh" },
      ],
      Amritsar: [{ id: "pb-amr-1", name: "District Court, Amritsar" }],
      Ludhiana: [{ id: "pb-lud-1", name: "District Court, Ludhiana" }],
    },
    Rajasthan: {
      Jaipur: [
        { id: "rj-jai-1", name: "Rajasthan High Court" },
        { id: "rj-jai-2", name: "District Court, Jaipur" },
      ],
      Jodhpur: [{ id: "rj-jod-1", name: "District Court, Jodhpur" }],
      Udaipur: [{ id: "rj-uda-1", name: "District Court, Udaipur" }],
      Ajmer: [{ id: "rj-ajm-1", name: "District Court, Ajmer" }],
    },
    Sikkim: {
      Gangtok: [
        { id: "sk-gan-1", name: "High Court of Sikkim" },
        { id: "sk-gan-2", name: "District Court, Gangtok" },
      ],
    },
    "Tamil Nadu": {
      Chennai: [
        { id: "tn-che-1", name: "Madras High Court" },
        { id: "tn-che-2", name: "District Court, Chennai" },
      ],
      Madurai: [{ id: "tn-mad-1", name: "District Court, Madurai" }],
      Coimbatore: [{ id: "tn-coi-1", name: "District Court, Coimbatore" }],
      Salem: [{ id: "tn-sal-1", name: "District Court, Salem" }],
    },
    Telangana: {
      Hyderabad: [
        { id: "tg-hyd-1", name: "Hyderabad High Court" },
        { id: "tg-hyd-2", name: "District Court, Hyderabad" },
      ],
      Warangal: [{ id: "tg-war-1", name: "District Court, Warangal" }],
    },
    Tripura: {
      Agartala: [
        { id: "tr-aga-1", name: "High Court of Tripura" },
        { id: "tr-aga-2", name: "District Court, Agartala" },
      ],
    },
    "Uttar Pradesh": {
      Lucknow: [
        { id: "up-luc-1", name: "Allahabad High Court, Lucknow Bench" },
        { id: "up-luc-2", name: "District Court, Lucknow" },
      ],
      Kanpur: [{ id: "up-kan-1", name: "District Court, Kanpur" }],
      Varanasi: [{ id: "up-var-1", name: "District Court, Varanasi" }],
      Allahabad: [{ id: "up-all-1", name: "District Court, Allahabad" }],
    },
    Uttarakhand: {
      Dehradun: [
        { id: "ut-deh-1", name: "High Court of Uttarakhand" },
        { id: "ut-deh-2", name: "District Court, Dehradun" },
      ],
      Nainital: [{ id: "ut-nai-1", name: "District Court, Nainital" }],
    },
    "West Bengal": {
      Kolkata: [
        { id: "wb-kol-1", name: "Calcutta High Court" },
        { id: "wb-kol-2", name: "District Court, Kolkata" },
      ],
      Darjeeling: [{ id: "wb-dar-1", name: "District Court, Darjeeling" }],
      Asansol: [{ id: "wb-asa-1", name: "District Court, Asansol" }],
    },
  }

  console.log("[v0] Fetching courts for state:", state, "district:", district)
  const courts = courtsByLocation[state || ""]?.[district || ""] || []
  console.log("[v0] Found courts:", courts)

  return Response.json({ courts })
}
