import React from "react";

export const StatCardSkeleton = ({ compact }) => (
  <div className={`bg-white dark:bg-[#1A1E27] rounded-2xl ${compact ? 'p-3' : 'p-5'} border border-slate-100 dark:border-white/[0.08] shadow-card dark:shadow-card-dark shimmer-animation`}>
    <div className={`flex justify-between items-start ${compact ? 'mb-2' : 'mb-4'}`}>
      <div className={`${compact ? 'w-8 h-8' : 'w-10 h-10'} rounded-xl bg-slate-100 dark:bg-slate-800`} />
      <div className={`${compact ? 'w-4 h-4' : 'w-5 h-5'} rounded bg-slate-100 dark:bg-slate-800`} />
    </div>
    <div className={`w-24 h-4 bg-slate-100 dark:bg-slate-800 rounded ${compact ? 'mb-1' : 'mb-2'}`} />
    <div className={`w-28 ${compact ? 'h-6' : 'h-8'} bg-slate-200 dark:bg-slate-700/60 rounded ${compact ? 'mb-2' : 'mb-3'}`} />
    <div className="w-20 h-4 bg-slate-100 dark:bg-slate-800 rounded" />
  </div>
);

export const MapSkeleton = () => (
  <div className="bg-white dark:bg-[#1A1E27] rounded-2xl p-6 border border-slate-100 dark:border-white/[0.08] shadow-card dark:shadow-card-dark h-[500px] shimmer-animation flex flex-col justify-between">
    <div className="flex justify-between items-center">
      <div className="w-48 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="w-28 h-8 bg-slate-100 dark:bg-slate-800 rounded-lg" />
    </div>
    <div className="w-full h-72 bg-slate-100 dark:bg-slate-800/80 rounded-2xl flex items-center justify-center">
      <div className="w-12 h-12 rounded-full border-4 border-slate-200 dark:border-slate-700 border-t-blue-500 animate-spin" />
    </div>
    <div className="flex gap-4">
      <div className="w-32 h-6 bg-slate-100 dark:bg-slate-800 rounded" />
      <div className="w-32 h-6 bg-slate-100 dark:bg-slate-800 rounded" />
    </div>
  </div>
);

export const FeedSkeleton = () => (
  <div className="bg-white dark:bg-[#1A1E27] rounded-2xl p-6 border border-slate-100 dark:border-white/[0.08] shadow-card dark:shadow-card-dark h-[500px] shimmer-animation flex flex-col">
    <div className="flex justify-between items-center mb-6">
      <div className="w-36 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="w-16 h-4 bg-slate-100 dark:bg-slate-800 rounded" />
    </div>
    <div className="space-y-4 flex-1">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="p-3.5 rounded-xl border border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div>
              <div className="w-32 h-4 bg-slate-200 dark:bg-slate-700 rounded mb-1.5" />
              <div className="w-44 h-3 bg-slate-100 dark:bg-slate-800 rounded" />
            </div>
          </div>
          <div className="flex flex-col items-end gap-1.5">
            <div className="w-16 h-5 bg-slate-200 dark:bg-slate-700 rounded-full" />
            <div className="w-12 h-3 bg-slate-100 dark:bg-slate-800 rounded" />
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const ChartSkeleton = () => (
  <div className="bg-white dark:bg-[#1A1E27] rounded-2xl p-6 border border-slate-100 dark:border-white/[0.08] shadow-card dark:shadow-card-dark h-[380px] shimmer-animation flex flex-col justify-between">
    <div className="flex justify-between items-center">
      <div className="w-36 h-6 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="w-24 h-8 bg-slate-100 dark:bg-slate-800 rounded-lg" />
    </div>
    <div className="w-full h-52 bg-slate-100 dark:bg-slate-800/80 rounded-2xl" />
    <div className="flex justify-around">
      <div className="w-16 h-3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="w-16 h-3 bg-slate-200 dark:bg-slate-700 rounded" />
      <div className="w-16 h-3 bg-slate-200 dark:bg-slate-700 rounded" />
    </div>
  </div>
);
