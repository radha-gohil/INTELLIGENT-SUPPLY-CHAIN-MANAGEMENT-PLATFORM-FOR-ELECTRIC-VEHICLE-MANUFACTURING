import {
  createContext,
  useContext,
  useEffect,
  useState
} from "react";

import {
  getAuthToken,
  getCurrentUser,
  loginUser,
  logoutUser,
  setAuthToken
} from "../services/api";


const AuthContext =
  createContext(null);


// ============================================================
// AUTH PROVIDER
// ============================================================

export function AuthProvider({
  children
}) {

  const [
    user,
    setUser
  ] = useState(null);


  const [
    loading,
    setLoading
  ] = useState(true);


  // ==========================================================
  // RESTORE LOGIN
  // ==========================================================

  useEffect(() => {

    const restoreSession =
      async () => {

        const token =
          getAuthToken();


        if (!token) {

          setLoading(false);

          return;

        }


        try {

          const currentUser =
            await getCurrentUser();


          setUser(
            currentUser
          );

        }
        catch {

          logoutUser();

          setUser(
            null
          );

        }
        finally {

          setLoading(false);

        }

      };


    restoreSession();

  }, []);


  // ==========================================================
  // LOGIN
  // ==========================================================

  const login =
    async (
      email,
      password
    ) => {

      const result =
        await loginUser(
          email,
          password
        );


      setAuthToken(
        result.access_token
      );


      setUser(
        result.user
      );


      return result.user;

    };


  // ==========================================================
  // LOGOUT
  // ==========================================================

  const logout = () => {

    logoutUser();

    setUser(
      null
    );

  };


  return (

    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isAuthenticated:
          Boolean(user)
      }}
    >

      {children}

    </AuthContext.Provider>

  );

}


// ============================================================
// HOOK
// ============================================================

export function useAuth() {

  const context =
    useContext(
      AuthContext
    );


  if (!context) {

    throw new Error(
      "useAuth must be used inside AuthProvider."
    );

  }


  return context;

}