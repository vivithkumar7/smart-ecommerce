import {
  Link,
  useNavigate,
} from "react-router-dom";

import "../styles/navbar.css";


export default function Navbar({
  cartCount,
}) {

  const navigate =
    useNavigate();


  const token =
    localStorage.getItem(
      "access_token"
    );


  const handleLogout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "token_type"
    );

    navigate("/login");

  };


  return (

    <nav className="navbar">

      <div className="navbar-container">


        <Link
          to="/"
          className="navbar-logo"
        >
          SmartShop
        </Link>


        <div className="navbar-links">


          {token && (

            <>

              <Link to="/">
                Products
              </Link>


              <Link to="/cart">

                🛒 Cart

                {cartCount > 0 && (

                  <span className="cart-count">
                    {cartCount}
                  </span>

                )}

              </Link>


              <button
                onClick={handleLogout}
                className="logout-button"
              >
                Logout
              </button>

            </>

          )}


        </div>

      </div>

    </nav>

  );
}