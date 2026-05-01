import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyATZanHFYEpBIrDAPmukfhsS7WwwtkuEPU",
  authDomain: "waste-management-sysytem.firebaseapp.com",
  projectId: "waste-management-sysytem",
  storageBucket: "waste-management-sysytem.firebasestorage.app",
  messagingSenderId: "224436434885",
  appId: "1:224436434885:web:9b512f2959ffa08012bdac",
  measurementId: "G-ZXD6X41V09"
};

const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);