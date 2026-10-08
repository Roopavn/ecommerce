function getCookie(name) {
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (const cookie of cookies) {
        const [key, ...value] = cookie.trim().split("=");
        if (key === name) return decodeURIComponent(value.join("="));
    }
    return null;
}

function readCart() {
    try {
        return JSON.parse(getCookie("cart") || "{}");
    } catch {
        return {};
    }
}

function writeCart(cart) {
    document.cookie = "cart=" + encodeURIComponent(JSON.stringify(cart)) + ";path=/;SameSite=Lax";
}

function updateCart(productId, action) {
    const cart = readCart();
    const key = String(productId);

    if (!cart[key]) cart[key] = {quantity: 0};
    cart[key].quantity += action === "add" ? 1 : -1;

    if (cart[key].quantity <= 0) delete cart[key];
    writeCart(cart);

    window.location.reload();
}

document.querySelectorAll(".update-cart").forEach((button) => {
    button.addEventListener("click", () => {
        updateCart(button.dataset.product, button.dataset.action);
    });
});
