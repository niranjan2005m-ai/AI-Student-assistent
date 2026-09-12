import { BrainCircuit } from "lucide-react";
import { motion } from "framer-motion";

function Hero() {
  return (
    <div className="text-center">

      <h2 className="text-5xl font-semibold tracking-tight text-white">
        Hi,How can I help ?
      </h2>

      <p className="mx-auto mt-3 max-w-xl text-base leading-7 text-slate-400">
        Upload your document and study with an adaptive AI tutor.
      </p>

    </div>
  );
}

export default Hero;