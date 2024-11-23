import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import {
  getFirestore,
  collection,
  query,
  where,
  getDocs,
} from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyA3_v6ZaVv5TSjQD4lGfu7H_F9BpM2idnQ",
  authDomain: "ratemyschedule-c9fab.firebaseapp.com",
  databaseURL: "https://ratemyschedule-c9fab-default-rtdb.firebaseio.com",
  projectId: "ratemyschedule-c9fab",
  storageBucket: "ratemyschedule-c9fab.firebasestorage.app",
  messagingSenderId: "556409279427",
  appId: "1:556409279427:web:d63b41188a64bf66f2e376",
  measurementId: "G-Y10BB59QJP",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);

import { db, collection, query, where, getDocs } from "./firebase-init.js";
