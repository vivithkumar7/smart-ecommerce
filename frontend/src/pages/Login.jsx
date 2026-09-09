import { useState } from "react";

import { useNavigate } from "react-router-dom";

import { loginUser, signupUser } from "../api/authApi";

import "../styles/login.css";


export default function Login() {

  const navigate = useNavigate();


  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [isRegistering, setIsRegistering] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const handleSubmit = async (event) => {

    event.preventDefault();

    setError("");

    setLoading(true);


    try {

      const data = isRegistering
        ? await signupUser(email, password)
        : await loginUser(email, password);


      console.log(
        "Login response:",
        data
      );


      if (!data.access_token) {

        throw new Error(
          "Access token was not returned."
        );

      }


      localStorage.setItem(
        "access_token",
        data.access_token
      );


      localStorage.setItem(
        "token_type",
        data.token_type || "bearer"
      );
      if (data.user_id) localStorage.setItem("user_id", data.user_id);


      if (isRegistering) {
        const loginData = await loginUser(email, password);
        localStorage.setItem("access_token", loginData.access_token);
        localStorage.setItem("token_type", loginData.token_type || "bearer");
        if (loginData.user_id) localStorage.setItem("user_id", loginData.user_id);
      } else {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("token_type", data.token_type || "bearer");
        if (data.user_id) localStorage.setItem("user_id", data.user_id);
      }

      navigate("/");

    } catch (error) {

      console.error(error);


      const message =
        error.response?.data?.detail ||
        error.message ||
        "Login failed.";


      setError(message);

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="login-page">

      <section className="login-showcase" aria-label="SmartShop collection">
        <div className="showcase-topline">
          <span className="showcase-mark">S</span>
          <span>SmartShop</span>
        </div>

        <div className="showcase-copy">
          <p className="showcase-kicker">A better way to shop</p>
          <h2>Find pieces that feel like you.</h2>
          <p>Curated products, thoughtful details, and a smoother everyday checkout.</p>
        </div>

        <div className="showcase-art" aria-hidden="true">
          <div className="art-orbit art-orbit-one" />
          <div className="art-orbit art-orbit-two" />
          <div className="art-product art-product-back" />
          <div className="art-product art-product-front">
            <span className="art-product-label">NEW<br />SEASON</span>
          </div>
          <span className="art-spark spark-one">+</span>
          <span className="art-spark spark-two">+</span>
        </div>

        <div className="showcase-footer">
          <span>01</span>
          <span className="showcase-line" />
          <span>Everyday essentials</span>
        </div>
      </section>

      <div className="login-card">

        <div className="login-header">

          <h1>
            SmartShop
          </h1>

          <p>
            {isRegistering ? "Create your account" : "Login to your account"}
          </p>

        </div>


        <form
          onSubmit={handleSubmit}
          className="login-form"
        >

          {error && (

            <div className="login-error">
              {error}
            </div>

          )}


          <div className="form-group">

            <label>
              Email Address
            </label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              required
            />

          </div>


          <div className="form-group">

            <label>
              Password
            </label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              required
            />

          </div>


          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >

            {loading
              ? (isRegistering ? "Creating account..." : "Logging in...")
              : (isRegistering ? "Register" : "Login")}

          </button>

        </form>

        <p className="login-signup">
          {isRegistering ? "Already have an account?" : "Don't have an account?"}
          <button
            className="login-signup-button"
            onClick={() => {
              setIsRegistering((current) => !current);
              setError("");
            }}
            type="button"
          >
            {isRegistering ? "Login" : "Register"}
          </button>
        </p>

      </div>

    </div>

  );
}