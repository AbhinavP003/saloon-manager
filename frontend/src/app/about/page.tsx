import Link from "next/link";

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-neutral-950 text-white pt-32 px-6 pb-20">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-4xl font-bold tracking-tight mb-6">About Saloon Manager</h1>
        <p className="text-neutral-400 leading-relaxed mb-4">
          Saloon Manager is a beta marketplace for discovering local salons, booking
          appointments in real time, and managing bookings as a salon owner.
        </p>
        <p className="text-neutral-400 leading-relaxed mb-8">
          This deployment is for testing with peers. Features include store discovery,
          service menus, live slot availability, customer accounts, and an owner dashboard
          with booking status workflow and monthly analytics.
        </p>
        <Link
          href="/"
          className="inline-flex h-11 px-6 items-center rounded-full bg-white text-black text-sm font-bold hover:bg-neutral-200 transition-colors"
        >
          Explore Salons
        </Link>
      </div>
    </main>
  );
}
