export const apiUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

export async function checked(response: Response): Promise<Response> {
  if (response.ok) return response;
  let message = "The request could not be completed.";
  try {
    const body = await response.json();
    if (typeof body.detail === "string") message = body.detail;
  } catch {}
  throw new Error(message);
}
