"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";

import { AuthAlert } from "@/components/auth/auth-alert";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSignup } from "@/hooks/auth/use-signup";
import { ROUTES } from "@/lib/constants";
import {
  signupSchema,
  slugifyOrganizationName,
  type SignupFormValues,
} from "@/lib/validations/auth";

export default function SignupForm() {
  const signup = useSignup();
  const [slugTouched, setSlugTouched] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      organization_name: "",
      organization_slug: "",
      full_name: "",
      email: "",
      password: "",
      confirm_password: "",
    },
  });

  const organizationName = watch("organization_name");

  useEffect(() => {
    if (!slugTouched && organizationName) {
      setValue("organization_slug", slugifyOrganizationName(organizationName), {
        shouldValidate: false,
      });
    }
  }, [organizationName, slugTouched, setValue]);

  return (
    <AuthCard>
      <form
        onSubmit={handleSubmit((values) => signup.mutate(values))}
        className="space-y-4"
        noValidate
      >
        <Input
          label="Organization name"
          autoComplete="organization"
          error={errors.organization_name?.message}
          {...register("organization_name")}
        />
        <Input
          label="Organization slug"
          placeholder="acme"
          error={errors.organization_slug?.message}
          {...register("organization_slug", {
            onChange: () => setSlugTouched(true),
          })}
        />
        <Input
          label="Full name"
          autoComplete="name"
          error={errors.full_name?.message}
          {...register("full_name")}
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
          autoComplete="new-password"
          error={errors.password?.message}
          {...register("password")}
        />
        <Input
          label="Confirm password"
          type="password"
          autoComplete="new-password"
          error={errors.confirm_password?.message}
          {...register("confirm_password")}
        />

        {signup.isError && <AuthAlert error={signup.error} />}

        <Button type="submit" className="w-full" loading={signup.isPending}>
          Create account
        </Button>
      </form>
      <p className="mt-6 text-center text-sm text-muted">
        Already have an account?{" "}
        <Link href={ROUTES.login} className="font-medium text-brand-600 hover:underline">
          Sign in
        </Link>
      </p>
    </AuthCard>
  );
}
