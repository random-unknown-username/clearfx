import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getFirestore, collection, addDoc, getDocs, doc, setDoc, query, orderBy } from "firebase/firestore";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyA-vzG2pfA5XwtIokevl8ccnnebb9Dg5IY",
  authDomain: "clearfx-29744.firebaseapp.com",
  projectId: "clearfx-29744",
  storageBucket: "clearfx-29744.firebasestorage.app",
  messagingSenderId: "376355063513",
  appId: "1:376355063513:web:cb62c9b5f25c0141db20c8",
  measurementId: "G-MB3LKWDLY3"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();

export { signInWithPopup, signOut, collection, addDoc, getDocs, doc, setDoc, query, orderBy };
