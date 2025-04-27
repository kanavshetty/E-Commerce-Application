import { Link } from 'react-router-dom';

function Header() {
  return (
    <header style={{ backgroundColor: '#333', padding: '1rem', color: 'white' }}>
      <nav>
        <Link to="/" style={{ color: 'white', margin: '0 1rem' }}>Home</Link>
        <Link to="/cart" style={{ color: 'white', margin: '0 1rem' }}>Cart</Link>
        <Link to="/login" style={{ color: 'white', margin: '0 1rem' }}>Login</Link>
        <Link to="/register" style={{ color: 'white', margin: '0 1rem' }}>Register</Link>
        <Link to="/dashboard" style={{ color: 'white', margin: '0 1rem' }}>Dashboard</Link>
        <Link to="/orders" style={{ color: 'white', margin: '0 1rem' }}>Orders</Link>
      </nav>
    </header>
  );
}

export default Header;
