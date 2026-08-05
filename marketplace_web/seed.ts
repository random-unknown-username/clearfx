import { initializeApp } from "firebase/app";
import { getFirestore, doc, setDoc } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyA-vzG2pfA5XwtIokevl8ccnnebb9Dg5IY",
  authDomain: "clearfx-29744.firebaseapp.com",
  projectId: "clearfx-29744",
  storageBucket: "clearfx-29744.firebasestorage.app",
  messagingSenderId: "376355063513",
  appId: "1:376355063513:web:cb62c9b5f25c0141db20c8",
  measurementId: "G-MB3LKWDLY3"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

const dummyDesigns = [
  { slug: 'matrix-rain', name: 'Matrix Digital Rain', desc: 'Classic falling green code effect with varying speeds.' },
  { slug: 'starfield-warp', name: 'Starfield Warp', desc: 'Hyperspace jump effect flying through a field of stars.' },
  { hack: 'hacker-typing', slug: 'sys-boot', name: 'System Boot Sequence', desc: 'Simulated retro OS boot sequence with random hex dumps.' },
  { slug: 'neon-waves', name: 'Neon Synthwave', desc: 'Retro 80s grid with a neon sun and scanlines.' },
  { slug: 'fire-particles', name: 'Campfire', desc: 'Cozy ascii fire animation burning at the bottom of your screen.' },
  { slug: 'snow-fall', name: 'Blizzard', desc: 'Heavy snow falling across the terminal with wind effects.' },
  { slug: 'glitch-art', name: 'Glitch Text', desc: 'Corrupted text blocks that randomly glitch and tear.' },
  { slug: 'radar-sweep', name: 'Submarine Radar', desc: 'Classic sweeping green radar detecting blips.' },
  { slug: 'conways-game', name: 'Game of Life', desc: 'Conways Game of Life cellular automaton running briefly.' },
  { slug: 'dvd-bounce', name: 'DVD Logo', desc: 'The iconic bouncing DVD logo hitting the corners.' }
];

async function seed() {
  console.log("Seeding 10 designs by Rand0m_unkn0wn...");
  for (let i = 0; i < dummyDesigns.length; i++) {
    const d = dummyDesigns[i];
    await setDoc(doc(db, 'designs', d.slug), {
      slug: d.slug,
      name: d.name,
      description: d.desc,
      author_uid: 'dummy-uid-12345',
      author_handle: 'Rand0m_unkn0wn',
      upvotes_count: Math.floor(Math.random() * 500) + 10
    });
    console.log(`Added ${d.slug}`);
  }
  console.log("Done!");
  process.exit(0);
}

seed().catch(console.error);
