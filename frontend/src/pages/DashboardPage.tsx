import { useDashboard, useRegimeHistory, useTriggerFetch, useFetchStatus } from '../hooks/useMacro';
import RegimeQuadrant from '../components/RegimeQuadrant';
import CompositeGauge from '../components/CompositeGauge';
import CategoryCard from '../components/CategoryCard';
import IndicatorTable from '../components/IndicatorTable';
import RegimeTimeline from '../components/RegimeTimeline';

function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="text-xs" style={{ color: '#585b70' }}>
      {'\u2500\u2500'} {children} {'\u2500'.repeat(60)}
    </div>
  );
}

function Loading() {
  return <div className="text-xs animate-pulse" style={{ color: '#585b70' }}>loading...</div>;
}

function ErrorMsg({ message }: { message: string }) {
  return <div className="text-xs" style={{ color: '#f38ba8' }}>error: {message}</div>;
}

export default function DashboardPage() {
  const { data: dashboard, isLoading, error } = useDashboard();
  const { data: regimeHistory } = useRegimeHistory();
  const { data: fetchStatus } = useFetchStatus();
  const triggerFetch = useTriggerFetch();

  const regime = dashboard?.regime ?? null;
  const categoryScores = regime?.component_scores?.category_scores as Record<string, number> | undefined;

  return (
    <div className="min-h-screen" style={{ background: '#1e1e2e', color: '#cdd6f4' }}>
      <div className="max-w-[1400px] mx-auto px-4 py-4 space-y-5">
        {/* Header */}
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-lg font-bold tracking-wider" style={{ color: '#cdd6f4' }}>
              MACROSENTIMENT
            </h1>
            {regime && (
              <span
                className={`px-2 py-0.5 rounded-full text-[0.65rem] font-semibold border regime-bg-${regime.regime}`}
                style={{ color: regime.regime === 'goldilocks' ? '#a6e3a1' : regime.regime === 'reflation' ? '#f9e2af' : regime.regime === 'deflation' ? '#89b4fa' : '#f38ba8' }}
              >
                {regime.regime.toUpperCase()}
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            {dashboard?.last_updated && (
              <span className="text-[0.65rem]" style={{ color: '#585b70' }}>
                updated {new Date(dashboard.last_updated).toLocaleDateString()}
              </span>
            )}
            <button
              className="px-3 py-1 text-[0.65rem] rounded border"
              style={{ borderColor: '#313244', color: '#7f849c', background: 'transparent' }}
              onClick={() => triggerFetch.mutate()}
              disabled={triggerFetch.isPending}
            >
              {triggerFetch.isPending ? 'fetching...' : 'refresh data'}
            </button>
          </div>
        </header>

        {isLoading && <Loading />}
        {error && <ErrorMsg message={(error as Error).message} />}

        {dashboard && (
          <>
            {/* Hero Section: Regime Quadrant + Composite Score */}
            <section>
              <SectionHeading>REGIME & SCORE</SectionHeading>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-2">
                <div className="rounded border p-4" style={{ background: '#181825', borderColor: '#313244' }}>
                  <div className="text-[0.65rem] font-semibold tracking-wider mb-2" style={{ color: '#7f849c' }}>
                    REGIME QUADRANT
                  </div>
                  <RegimeQuadrant
                    current={regime}
                    history={regimeHistory?.snapshots}
                  />
                </div>
                <div className="rounded border p-4" style={{ background: '#181825', borderColor: '#313244' }}>
                  <div className="text-[0.65rem] font-semibold tracking-wider mb-2" style={{ color: '#7f849c' }}>
                    COMPOSITE SENTIMENT
                  </div>
                  <CompositeGauge
                    regime={regime}
                    compositeScore={dashboard.composite_score}
                    categoryScores={categoryScores}
                  />
                </div>
              </div>
            </section>

            {/* Category Cards */}
            {dashboard.categories.length > 0 && (
              <section>
                <SectionHeading>CATEGORIES</SectionHeading>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 mt-2">
                  {dashboard.categories.map((cat) => (
                    <CategoryCard key={cat.name} category={cat} />
                  ))}
                </div>
              </section>
            )}

            {/* Indicator Table */}
            {dashboard.indicators.length > 0 && (
              <section>
                <SectionHeading>ALL INDICATORS</SectionHeading>
                <div className="mt-2">
                  <IndicatorTable indicators={dashboard.indicators} />
                </div>
              </section>
            )}

            {/* Regime History Timeline */}
            <section>
              <SectionHeading>REGIME HISTORY</SectionHeading>
              <div className="mt-2 rounded border p-4" style={{ background: '#181825', borderColor: '#313244' }}>
                <RegimeTimeline />
              </div>
            </section>

            {/* Fetch Status */}
            {fetchStatus && (
              <section>
                <SectionHeading>DATA SOURCES</SectionHeading>
                <div className="flex gap-4 mt-2">
                  {fetchStatus.map((fs) => (
                    <div
                      key={fs.source}
                      className="text-[0.65rem] px-3 py-1.5 rounded border"
                      style={{ background: '#181825', borderColor: '#313244' }}
                    >
                      <span style={{ color: '#7f849c' }}>{fs.source.toUpperCase()}</span>{' '}
                      <span style={{ color: fs.status === 'success' ? '#a6e3a1' : fs.status === 'error' ? '#f38ba8' : '#585b70' }}>
                        {fs.status || 'pending'}
                      </span>
                      {fs.last_fetch && (
                        <span style={{ color: '#585b70' }}>
                          {' '}{new Date(fs.last_fetch).toLocaleString()}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </div>
    </div>
  );
}
