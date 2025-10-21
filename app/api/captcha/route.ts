export async function GET() {
  // Generate a random 6-character alphanumeric captcha code
  const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
  let captchaCode = ""
  for (let i = 0; i < 6; i++) {
    captchaCode += characters.charAt(Math.floor(Math.random() * characters.length))
  }

  // Generate a unique session ID for this captcha
  const sessionId = Math.random().toString(36).substring(2, 15)

  return Response.json({
    captchaCode,
    sessionId,
    expiresAt: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 minutes expiry
  })
}
