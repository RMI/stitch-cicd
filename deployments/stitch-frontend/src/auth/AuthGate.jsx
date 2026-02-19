import { useEffect } from "react";
import { useAuth0 } from "@auth0/auth0-react";

export default function AuthGate({ children }) {
  const { isLoading, isAuthenticated, error, loginWithRedirect } = useAuth0();

  useEffect(() => {
    if (!isLoading && !isAuthenticated && !error) {
      loginWithRedirect();
    }
  }, [isLoading, isAuthenticated, error, loginWithRedirect]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500 text-lg">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-red-600 text-lg">
          Authentication error: {error.message}
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return children;
}
