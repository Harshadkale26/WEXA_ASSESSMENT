"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useForm } from "react-hook-form";

import { AuthAlert } from "@/components/auth/auth-alert";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useLogin } from "@/hooks/auth/use-login";
import { ROUTES } from "@/lib/constants";
import { loginSchema, type LoginFormValues } from "@/lib/validations/auth";

export default function LoginForm() {
  const login = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      organization_slug: "",
      email: "",
      password: "",
    },
  });

  return (
    <AuthCard>
      <form
        onSubmit={handleSubmit((values) => login.mutate(values))}
        className="space-y-5"
        noValidate
      >
        <Input
          label="Organization slug"
          placeholder="acme"
          autoComplete="organization"
          error={errors.organization_slug?.message}
          {...register("organization_slug")}
        />
        <Input
          label="Email"
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register("email")}
        />
        <Input
          label="Password"
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register("password")}
        />

        {login.isError && <AuthAlert error={login.error} />}

        <Button type="submit" className="w-full" loading={login.isPending}>
          Sign in
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        No account?{" "}
        <Link href={ROUTES.signup} className="font-medium text-brand-600 hover:underline">
          Create organization
        </Link>
      </p>
    </AuthCard>
  );
}
