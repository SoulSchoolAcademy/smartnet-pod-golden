export async function signupFlow(input: { email: string }) {
  return { userId: `u_${Date.now()}`, email: input.email };
}
