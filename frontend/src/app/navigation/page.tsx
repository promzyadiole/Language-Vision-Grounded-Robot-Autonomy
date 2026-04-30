"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getEnvironment,
  getNavigationPlaces,
  goToPlace,
  initializeLocalization,
  type EnvironmentConfig,
  type PlacePose,
} from "@/lib/api";

type PlacesRecord = Record<string, PlacePose>;

const PLACE_STYLES: Record<
  string,
  {
    active: string;
    inactive: string;
    soft: string;
  }
> = {
  entrance: {
    active: "border-indigo-700 bg-indigo-700 text-white shadow-indigo-200",
    inactive:
      "border-indigo-200 bg-indigo-50 text-indigo-900 hover:border-indigo-300 hover:bg-indigo-100",
    soft: "bg-indigo-50 text-indigo-900",
  },
  dining: {
    active: "border-violet-700 bg-violet-700 text-white shadow-violet-200",
    inactive:
      "border-violet-200 bg-violet-50 text-violet-900 hover:border-violet-300 hover:bg-violet-100",
    soft: "bg-violet-50 text-violet-900",
  },
  kitchen: {
    active: "border-amber-600 bg-amber-600 text-white shadow-amber-200",
    inactive:
      "border-amber-200 bg-amber-50 text-amber-900 hover:border-amber-300 hover:bg-amber-100",
    soft: "bg-amber-50 text-amber-900",
  },
  hallway: {
    active: "border-emerald-700 bg-emerald-700 text-white shadow-emerald-200",
    inactive:
      "border-emerald-200 bg-emerald-50 text-emerald-900 hover:border-emerald-300 hover:bg-emerald-100",
    soft: "bg-emerald-50 text-emerald-900",
  },
  front_room: {
    active: "border-sky-700 bg-sky-700 text-white shadow-sky-200",
    inactive:
      "border-sky-200 bg-sky-50 text-sky-900 hover:border-sky-300 hover:bg-sky-100",
    soft: "bg-sky-50 text-sky-900",
  },
  sitting_room: {
    active: "border-rose-700 bg-rose-700 text-white shadow-rose-200",
    inactive:
      "border-rose-200 bg-rose-50 text-rose-900 hover:border-rose-300 hover:bg-rose-100",
    soft: "bg-rose-50 text-rose-900",
  },
  parlour: {
    active: "border-pink-700 bg-pink-700 text-white shadow-pink-200",
    inactive:
      "border-pink-200 bg-pink-50 text-pink-900 hover:border-pink-300 hover:bg-pink-100",
    soft: "bg-pink-50 text-pink-900",
  },
  gym_room: {
    active: "border-cyan-700 bg-cyan-700 text-white shadow-cyan-200",
    inactive:
      "border-cyan-200 bg-cyan-50 text-cyan-900 hover:border-cyan-300 hover:bg-cyan-100",
    soft: "bg-cyan-50 text-cyan-900",
  },
  bedroom: {
    active: "border-fuchsia-700 bg-fuchsia-700 text-white shadow-fuchsia-200",
    inactive:
      "border-fuchsia-200 bg-fuchsia-50 text-fuchsia-900 hover:border-fuchsia-300 hover:bg-fuchsia-100",
    soft: "bg-fuchsia-50 text-fuchsia-900",
  },
  study_room: {
    active: "border-teal-700 bg-teal-700 text-white shadow-teal-200",
    inactive:
      "border-teal-200 bg-teal-50 text-teal-900 hover:border-teal-300 hover:bg-teal-100",
    soft: "bg-teal-50 text-teal-900",
  },
  visitors_room: {
    active: "border-orange-700 bg-orange-700 text-white shadow-orange-200",
    inactive:
      "border-orange-200 bg-orange-50 text-orange-900 hover:border-orange-300 hover:bg-orange-100",
    soft: "bg-orange-50 text-orange-900",
  },
  center_area: {
    active: "border-slate-800 bg-slate-800 text-white shadow-slate-200",
    inactive:
      "border-slate-300 bg-slate-50 text-slate-900 hover:border-slate-400 hover:bg-slate-100",
    soft: "bg-slate-50 text-slate-900",
  },
};

function formatPlaceLabel(place: string): string {
  return place
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getPlaceStyle(place: string) {
  return (
    PLACE_STYLES[place] ?? {
      active: "border-slate-900 bg-slate-900 text-white shadow-slate-200",
      inactive:
        "border-slate-300 bg-white text-slate-900 hover:border-slate-400 hover:bg-slate-50",
      soft: "bg-slate-50 text-slate-900",
    }
  );
}

function quaternionToYaw(qz: number, qw: number): number {
  return Math.atan2(2 * qw * qz, 1 - 2 * qz * qz);
}

export default function NavigationPage() {
  const [environment, setEnvironment] = useState<EnvironmentConfig | null>(null);
  const [places, setPlaces] = useState<PlacesRecord>({});
  const [selectedPlace, setSelectedPlace] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [busy, setBusy] = useState<boolean>(false);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);

        const [envRes, placesRes] = await Promise.all([
          getEnvironment(),
          getNavigationPlaces(),
        ]);

        setEnvironment(envRes.data ?? null);

        const loadedPlaces: PlacesRecord = placesRes.data?.places ?? {};
        setPlaces(loadedPlaces);

        const firstPlace = Object.keys(loadedPlaces)[0];
        if (firstPlace) {
          setSelectedPlace(firstPlace);
        }
      } catch (error) {
        setMessage(
          error instanceof Error
            ? error.message
            : "Failed to load navigation data."
        );
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const placeOptions = useMemo(() => Object.keys(places), [places]);
  const selectedPose = selectedPlace ? places[selectedPlace] : null;
  const selectedPlaceStyle = getPlaceStyle(selectedPlace);

  async function handleInitializeLocalization() {
    try {
      setBusy(true);
      setMessage("");
      const res = await initializeLocalization();
      setMessage(res.message ?? "Localization initialized.");
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Failed to initialize localization."
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleGoToPlace() {
    if (!selectedPlace) return;

    try {
      setBusy(true);
      setMessage("");
      const res = await goToPlace(selectedPlace);
      setMessage(
        res.message ?? `Navigation started for ${formatPlaceLabel(selectedPlace)}.`
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Failed to send navigation goal."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-100 via-blue-50 to-indigo-100 p-8">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="rounded-[2rem] border border-white/60 bg-white/90 p-8 shadow-xl shadow-slate-200/60 backdrop-blur">
          <h1 className="text-4xl font-bold tracking-tight text-slate-950">
            Navigation
          </h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-slate-700">
            Initialize localization and send semantic place navigation goals in the active environment.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <section className="rounded-[2rem] border border-white/60 bg-white/90 p-6 shadow-lg shadow-slate-200/60 backdrop-blur">
            <h2 className="text-2xl font-semibold text-slate-950">Environment</h2>

            {loading ? (
              <p className="mt-4 text-slate-500">Loading environment...</p>
            ) : (
              <div className="mt-5 space-y-4 text-slate-700">
                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
                    Active environment
                  </p>
                  <p className="mt-2 text-2xl font-semibold text-slate-950">
                    {environment?.name ?? "Unknown"}
                  </p>
                </div>

                <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
                    Map
                  </p>
                  <p className="mt-2 break-all text-sm leading-6 text-slate-800">
                    {environment?.navigation?.map_yaml_path ?? "Not available"}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleInitializeLocalization}
                  disabled={busy}
                  className="rounded-2xl bg-slate-950 px-5 py-3 font-medium text-white shadow-md shadow-slate-300 transition hover:opacity-90 disabled:opacity-60"
                >
                  {busy ? "Working..." : "Initialize Localization"}
                </button>
              </div>
            )}
          </section>

          <section className="rounded-[2rem] border border-white/60 bg-white/90 p-6 shadow-lg shadow-slate-200/60 backdrop-blur">
            <h2 className="text-2xl font-semibold text-slate-950">Places</h2>

            {loading ? (
              <p className="mt-4 text-slate-500">Loading places...</p>
            ) : (
              <div className="mt-5 space-y-5">
                <div>
                  <span className="mb-3 block text-sm font-medium uppercase tracking-wide text-slate-500">
                    Choose destination
                  </span>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {placeOptions.map((place) => {
                      const isSelected = selectedPlace === place;
                      const style = getPlaceStyle(place);

                      return (
                        <button
                          key={place}
                          type="button"
                          onClick={() => setSelectedPlace(place)}
                          className={`rounded-2xl border px-4 py-3 text-left font-medium transition shadow-sm ${
                            isSelected ? style.active : style.inactive
                          }`}
                        >
                          Go to {formatPlaceLabel(place)}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {selectedPose && (
                  <div
                    className={`rounded-3xl border border-white/60 p-5 ${selectedPlaceStyle.soft}`}
                  >
                    <p className="text-sm font-medium uppercase tracking-wide opacity-70">
                      Target pose
                    </p>
                    <p className="mt-3 text-lg">
                      <span className="font-semibold">x:</span>{" "}
                      {selectedPose.x.toFixed(2)}
                    </p>
                    <p className="text-lg">
                      <span className="font-semibold">y:</span>{" "}
                      {selectedPose.y.toFixed(2)}
                    </p>
                    <p className="text-lg">
                      <span className="font-semibold">qz:</span>{" "}
                      {selectedPose.qz.toFixed(3)}
                    </p>
                    <p className="text-lg">
                      <span className="font-semibold">qw:</span>{" "}
                      {selectedPose.qw.toFixed(3)}
                    </p>
                    <p className="text-lg">
                      <span className="font-semibold">yaw:</span>{" "}
                      {quaternionToYaw(selectedPose.qz, selectedPose.qw).toFixed(2)}
                    </p>
                  </div>
                )}

                <button
                  type="button"
                  onClick={handleGoToPlace}
                  disabled={busy || !selectedPlace}
                  className={`rounded-2xl px-5 py-3 font-medium shadow-md transition hover:opacity-90 disabled:opacity-60 ${
                    selectedPlace
                      ? selectedPlaceStyle.active
                      : "bg-slate-950 text-white"
                  }`}
                >
                  {busy
                    ? "Working..."
                    : selectedPlace
                    ? `Go To ${formatPlaceLabel(selectedPlace)}`
                    : "Go To Selected Place"}
                </button>
              </div>
            )}
          </section>
        </div>

        {message && (
          <div className="rounded-[2rem] border border-white/60 bg-white/90 p-6 shadow-lg shadow-slate-200/60 backdrop-blur">
            <h2 className="text-lg font-semibold text-slate-950">System Message</h2>
            <p className="mt-2 leading-7 text-slate-700">{message}</p>
          </div>
        )}
      </div>
    </main>
  );
}