export async function POST(request: Request) {
  try {
    const { documentId, fileName } = await request.json()

    if (!documentId || !fileName) {
      return Response.json({ error: "Missing documentId or fileName" }, { status: 400 })
    }

    // Simulate fetching PDF from eCourts or storage
    // In a real implementation, this would fetch from actual eCourts API or storage service
    const pdfBuffer = Buffer.from(
      "%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Sample PDF Document) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000244 00000 n\n0000000338 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n417\n%%EOF",
    )

    return new Response(pdfBuffer, {
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${fileName}.pdf"`,
        "Content-Length": pdfBuffer.length.toString(),
      },
    })
  } catch (error) {
    console.error("Download error:", error)
    return Response.json({ error: "Failed to download document" }, { status: 500 })
  }
}
