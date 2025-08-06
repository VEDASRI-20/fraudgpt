// src/firebase.js
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDhTrn_FBIN2zjQ1y7rXsjfAJxR60Vw3M8",
  authDomain: "fraudgpt-bc09f.firebaseapp.com",
  projectId: "fraudgpt-bc09f",
  storageBucket: "fraudgpt-bc09f.firebasestorage.app",
  messagingSenderId: "841959476329",
  appId: "1:841959476329:web:293d393fa117c27dbf26f8",
  measurementId: "G-X4ZZ9XGDRX"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
