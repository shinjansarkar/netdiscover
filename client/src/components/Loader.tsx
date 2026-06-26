import { Loader2 } from "lucide-react";

export default function Loader({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 space-y-6 w-full">
      <div className="relative">
        <div className="absolute inset-0 bg-[#CCFF00] translate-x-2 translate-y-2 border-4 border-brutal-black"></div>
        <div className="relative bg-white border-4 border-brutal-black p-5 flex items-center justify-center">
          <Loader2 size={64} className="animate-spin text-brutal-black" strokeWidth={3} />
        </div>
      </div>
      <div className="bg-brutal-black text-white px-6 py-3 font-mono text-xl uppercase tracking-widest animate-pulse border-[3px] border-brutal-black shadow-[4px_4px_0_0_#FF00FF]">
        {text}
      </div>
    </div>
  );
}
