function ProductCard({ product }) {
    return (
      <div style={{
        border: "1px solid #ccc",
        padding: "1rem",
        borderRadius: "8px",
        width: "250px"
      }}>
        <h3>{product.name}</h3>
        <p>Category: {product.category}</p>
        <p>Brand: {product.brand}</p>
        <p>Price: ${product.price}</p>
        <button>Add to Cart</button>
      </div>
    );
  }
  
  export default ProductCard;
  