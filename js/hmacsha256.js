const CryptoJS = require("crypto-js");

function calculateHMAC_SHA256(message, key) {
    return CryptoJS.HmacSHA256(message, key).toString(CryptoJS.enc.Hex);
}
