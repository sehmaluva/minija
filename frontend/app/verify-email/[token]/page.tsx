"use client";

import { useEffect, useState } from 'react';
import { userAPI } from '@/lib/api-functions';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function VerifyEmailPage() {
  const [message, setMessage] = useState('Verifying your email...');
  const [error, setError] = useState('');
  const params = useParams();
  const router = useRouter();
  const token = params.token as string;

  useEffect(() => {
    if (token) {
      userAPI.verifyEmail(token)
        .then(() => {
          setMessage('Email verified successfully! You will be redirected to the login page shortly.');
          setTimeout(() => router.push('/login'), 3000);
        })
        .catch(() => {
          setError('Invalid or expired verification link. Please request a new one.');
        });
    }
  }, [token, router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <CardTitle>Email Verification</CardTitle>
          <CardDescription>
            {error ? (
              <span className="text-red-600">{error}</span>
            ) : (
              <span className="text-gray-600 dark:text-gray-400">{message}</span>
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Link href="/login" className="text-sm text-blue-600 hover:underline">
              Go to Login
            </Link>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
