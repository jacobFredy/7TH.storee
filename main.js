console.log("JS WORKING");
function quickAdd(productId){
    fetch(`/quick_add/${productId}`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({quantity:1})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){

            let toast = document.getElementById('toast');
            if(toast){
                toast.textContent = "Товар доданий у корзину!";
                toast.style.display = "block";
                setTimeout(()=>{ toast.style.display="none"; }, 3000);
            }

            const cartCountElem = document.getElementById('cart-count');
            if(cartCountElem){
                cartCountElem.textContent = data.cart_count;

                const cartLink = document.getElementById('cart-link');
                if(cartLink){
                    cartLink.classList.add('cart-bounce');
                    setTimeout(()=>{
                        cartLink.classList.remove('cart-bounce');
                    },350);
                }
            }
        }
    })
}