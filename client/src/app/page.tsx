import Link from "next/link";
import { Skull, Zap, Eye, Crosshair } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-[calc(100vh-2rem)] flex flex-col items-center justify-center p-8 bg-[#F4F4F0] m-4 relative overflow-hidden font-mono border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)]">
      
      {/* Decorative Grid Background */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none"
        style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '40px 40px' }}
      ></div>

      <div className="max-w-5xl w-full z-10 flex flex-col items-center">
        
        {/* Header Section */}
        <div className="w-full flex flex-col items-center mb-16">
          <div className="bg-white border-4 border-black px-8 py-4 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transform -rotate-1 mb-8">
            <h1 className="text-6xl md:text-8xl font-black uppercase tracking-tighter text-center text-black leading-none">
              Net<span className="text-[#FF4F00]">Discover</span>
            </h1>
          </div>
          <div className="bg-black text-white px-6 py-2 transform rotate-1 border-4 border-black">
            <h2 className="text-xl md:text-2xl font-bold uppercase tracking-widest">
              Oh look, another network scanner.
            </h2>
          </div>
        </div>

        {/* Content Section */}
        <div className="w-full bg-white border-4 border-black shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] p-8 md:p-12 mb-16 relative">
          {/* Decorative elements */}
          <div className="absolute top-4 right-4 text-black">
            <Crosshair size={48} strokeWidth={1.5} className="opacity-20 animate-spin-slow" />
          </div>

          <p className="text-xl md:text-2xl font-bold leading-relaxed mb-10 max-w-3xl">
            Congratulations. You found a tool that pings IP addresses and checks if ports are open. 
            Groundbreaking stuff. Truly revolutionary. You're basically a cyber-warfare expert now.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 border-t-4 border-black pt-8 mt-8">
            <div className="group border-4 border-black p-6 bg-[#E0E7FF] hover:bg-[#FF4F00] hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1">
              <Zap size={40} strokeWidth={2.5} className="mb-4" />
              <h3 className="font-black uppercase text-xl mb-2">Fast</h3>
              <p className="text-sm font-bold opacity-90">It sends packets. Packets travel at the speed of light. Math.</p>
            </div>
            
            <div className="group border-4 border-black p-6 bg-[#D1FAE5] hover:bg-[#FF4F00] hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1">
              <Eye size={40} strokeWidth={2.5} className="mb-4" />
              <h3 className="font-black uppercase text-xl mb-2">Creepy</h3>
              <p className="text-sm font-bold opacity-90">See exactly what your roommates are leaving exposed on the WiFi.</p>
            </div>
            
            <div className="group border-4 border-black p-6 bg-[#FEE2E2] hover:bg-[#FF4F00] hover:text-white transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] hover:-translate-y-1">
              <Skull size={40} strokeWidth={2.5} className="mb-4" />
              <h3 className="font-black uppercase text-xl mb-2">Brutal</h3>
              <p className="text-sm font-bold opacity-90">No soft corners. If you cut yourself on the UI, that's your fault.</p>
            </div>
          </div>
        </div>

        {/* Call to action */}
        <div className="flex flex-col items-center">
          <Link 
            href="/dashboard" 
            className="group relative inline-block focus:outline-none"
          >
            <span className="absolute inset-0 bg-black translate-x-2 translate-y-2 transition-transform group-hover:translate-x-3 group-hover:translate-y-3"></span>
            <span className="relative inline-flex items-center justify-center bg-[#FF4F00] border-4 border-black px-12 py-6 text-2xl md:text-4xl font-black uppercase tracking-widest text-white transition-transform group-hover:-translate-x-1 group-hover:-translate-y-1">
              Enter The Matrix
              <span className="ml-4 animate-pulse">_</span>
            </span>
          </Link>
          
          <div className="mt-8 bg-black text-white px-4 py-2 border-2 border-dashed border-gray-500">
            <p className="font-mono text-xs font-bold uppercase tracking-wider">
              [ Click the obnoxiously large button to pretend you're a hacker from a 90s movie ]
            </p>
          </div>
        </div>

      </div>
    </div>
  );
}
