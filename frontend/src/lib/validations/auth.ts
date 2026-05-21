import { z } from "zod";

const slugRegex = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export const loginSchema = z.object({
  organization_slug: z
    .string()
    .min(2, "Organization slug must be at least 2 characters")
    .max(140, "Organization slug is too long")
    .regex(slugRegex, "Use lowercase letters, numbers, and hyphens only")
    .transform((v) => v.trim().toLowerCase()),
  email: z.string().min(1, "Email is required").email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export type LoginFormValues = z.infer<typeof loginSchema>;

export const signupSchema = z
  .object({
    organization_name: z
      .string()
      .min(2, "Organization name must be at least 2 characters")
      .max(120, "Organization name is too long"),
    organization_slug: z
      .string()
      .min(2, "Slug must be at least 2 characters")
      .max(140, "Slug is too long")
      .regex(slugRegex, "Use lowercase letters, numbers, and hyphens only")
      .transform((v) => v.trim().toLowerCase()),
    full_name: z
      .string()
      .min(2, "Full name must be at least 2 characters")
      .max(255, "Full name is too long"),
    email: z.string().min(1, "Email is required").email("Enter a valid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128, "Password is too long"),
    confirm_password: z.string().min(1, "Confirm your password"),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Passwords do not match",
    path: ["confirm_password"],
  });

export type SignupFormValues = z.infer<typeof signupSchema>;

export function slugifyOrganizationName(name: string): string {
  return name
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 140);
}
