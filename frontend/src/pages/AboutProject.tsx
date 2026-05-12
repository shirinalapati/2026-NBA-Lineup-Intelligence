/**
 * App home (`/`): narrative + technical methodology (ULS, simulator, traits), limitations.
 */

function CodeBlock({ children }: { children: string }) {
  return (
    <pre className="mt-3 mb-4 p-4 rounded-lg bg-court-950/80 dark:bg-black/40 border border-slate-700/80 text-slate-200 text-xs sm:text-sm font-mono overflow-x-auto leading-relaxed whitespace-pre-wrap">
      {children}
    </pre>
  )
}

export function AboutProject() {
  return (
    <article className="max-w-3xl space-y-12 text-slate-600 dark:text-slate-400 leading-relaxed">
      <header className="space-y-4">
        <h1 className="font-display text-3xl sm:text-4xl text-court-950 dark:text-white leading-tight">
          Lineup intelligence as transparent decision support
        </h1>
        <p className="text-lg text-slate-700 dark:text-slate-300">
          This app is built for people who care about{' '}
          <strong className="text-slate-800 dark:text-slate-200">how five players function as a unit</strong>—not only
          who tops a sortable table, but which combinations actually earn minutes, which efficient groups stay
          under-used, and how a single substitution might shift the statistical profile of a lineup.
        </p>
      </header>

      {/* ——— Narrative ——— */}
      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">1. The basketball problem</h2>
        <p>
          NBA lineup data is <strong className="text-slate-800 dark:text-slate-200">noisy, context-dependent, and hard
          to operationalize</strong> for rotation decisions. A five-man net rating tells you how that group performed in
          the minutes they shared—but not <em>why</em>, not against whom, and not whether the sample is stable enough to
          trust.
        </p>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Raw net rating is insufficient alone.</strong> It
            compresses offense and defense, hides minute totals, and rewards small samples that can swing with a few hot
            shooting nights.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Sample size is relentless.</strong> Rare lineups can
            look elite or awful by variance. The product uses minute floors and explicit scoring rules so users choose
            how much noise they tolerate.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Rotations are tradeoffs.</strong> Staggering stars,
            preserving spacing, hiding a weak defender, or closing with a defensive shell—all of that is a sequence of
            lineup choices, not one “best five.”
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Role overlap and substitution shape identity.</strong>{' '}
            Replacing one connector with another changes ball pressure, rim protection, and shot profile even when
            “talent” looks similar on paper.
          </li>
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">2. Why lineup analysis matters</h2>
        <p>
          Playoffs shorten rotations; matchups invite different frontiers; spacing and defensive versatility decide whether
          an offense can breathe; stagger patterns determine whether a star carries a weak bench or plays next to another
          creator. Lineup-level analysis is where{' '}
          <strong className="text-slate-800 dark:text-slate-200">offensive identity meets defensive coverage tradeoffs
          </strong>—where coaching staff actually live during games.
        </p>
        <p>
          Public tools often stop at player cards. This product keeps the{' '}
          <strong className="text-slate-800 dark:text-slate-200">five-man unit</strong> as the primary object so
          conversations about “this group” stay grounded in observed combinations and minutes, not hypothetical mixes.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">3. What the app attempts to solve</h2>
        <p className="text-slate-700 dark:text-slate-300 border-l-2 border-court-accent pl-4 py-1">
          The goal is <strong>not</strong> to perfectly predict future lineup performance. It is to offer a{' '}
          <strong className="text-court-950 dark:text-white">transparent framework</strong> for comparing lineup
          efficiency, usage patterns, and substitution dynamics—so analysts can triage questions, communicate tradeoffs,
          and stress-test intuition with interpretable numbers.
        </p>
        <p>In practice, the app supports workflows like:</p>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>Ranking and filtering units by net, offensive or defensive rating, minutes, or the composite Underrated Lineup Score you will see soon.</li>
          <li>Contrasting “best on paper” efficiency with “most used” groups—the rotation story versus the efficiency story.</li>
          <li>Running a directional substitution heuristic from an observed lineup baseline.</li>
        </ul>
        <h3 className="text-sm font-mono uppercase tracking-wider text-slate-500 dark:text-slate-500 pt-2">
          What coaches and ops might care about
        </h3>
        <p>
          The UI invites <strong className="text-slate-800 dark:text-slate-200">operational language</strong>: not “this
          model says win,” but “this unit sacrifices rim protection for spacing,” “this group posts strong efficiency but
          rarely plays together,” “this swap steepens the playmaking gradient while thinning perimeter pressure.” Those
          interpretations remain <em>human-led</em>; the app supplies structured signals so the story stays anchored in
          data you can inspect.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">4. Methodological philosophy</h2>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Transparency over black boxes.</strong> Weights and
            simulator coefficients are stated here and in code configuration.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Interpretability over overfitting.</strong> Simple
            transforms (min–max, explicit deltas) beat opaque scores that cannot be defended in a staff meeting.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Directional signals.</strong> Outputs are heuristics and
            comparisons—not calibrated win forecasts.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Operational usability.</strong> Filters, exports, and
            team views prioritize prep questions: who plays, who’s efficient, who’s under-used, what-if this swap.
          </li>
        </ul>
      </section>

      {/* Bridge */}
      <div className="rounded-xl border border-court-line/30 bg-court-line/5 dark:bg-court-line/10 px-5 py-4 text-slate-700 dark:text-slate-300 text-sm">
        <p className="font-mono text-xs uppercase tracking-wider text-court-line mb-2">How that becomes numbers</p>
        <p>
          The sections below are the <strong className="text-court-950 dark:text-white">technical specification</strong>{' '}
          implemented in the data pipeline and API—the same definitions the leaderboard, underrated view, and simulator
          rely on. If you only read one technical block, read{' '}
          <a href="#league-vs-app-metrics" className="text-court-accent hover:underline">
            League vs app metrics
          </a>
          ,{' '}
          <a href="#pace-and-tempo" className="text-court-accent hover:underline">
            Pace vs ratings
          </a>
          ,{' '}
          <a href="#uls-formula" className="text-court-accent hover:underline">
            ULS
          </a>
          , and{' '}
          <a href="#substitution-simulator" className="text-court-accent hover:underline">
            substitution
          </a>
          .
        </p>
      </div>

      <div
        id="league-vs-app-metrics"
        className="rounded-xl border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-court-900/60 px-5 py-4 text-sm text-slate-700 dark:text-slate-300 space-y-3 scroll-mt-24"
      >
        <p className="font-mono text-xs uppercase tracking-wider text-slate-500 dark:text-slate-400">
          League numbers vs app-only calculations
        </p>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-800 dark:text-slate-200">Tables &amp; leaderboards (Net, ORtg, DRtg, Pace):</strong>{' '}
            For live NBA ingest, these are <strong className="text-slate-800 dark:text-slate-200">read from NBA.com</strong>{' '}
            (<code className="font-mono text-xs">OFF_RATING</code>, <code className="font-mono text-xs">DEF_RATING</code>,{' '}
            <code className="font-mono text-xs">NET_RATING</code>, <code className="font-mono text-xs">PACE</code>, etc.) and
            stored as-is. This product <strong>does not replace</strong> the league’s lineup <strong>NET_RATING</strong> with
            its own alternate “true net” for those views.
          </li>
          <li>
            <strong className="text-slate-800 dark:text-slate-200">ULS:</strong> A <strong>separate composite score</strong>{' '}
            built from normalized inputs (including the ingested <code className="font-mono text-xs">net_rating</code> column).
            It is not an NBA-published statistic.
          </li>
          <li>
            <strong className="text-slate-800 dark:text-slate-200">Substitution simulator:</strong> The{' '}
            <code className="font-mono text-xs">ProjOff</code>, <code className="font-mono text-xs">ProjDef</code>, and{' '}
            <code className="font-mono text-xs">ProjNet</code> formulas below are <strong>this app’s heuristic only</strong>,
            run when you simulate a swap. <strong className="text-slate-800 dark:text-slate-200">ProjNet is not the same
            field</strong> as the <strong>Net</strong> column in lineup tables—it is “projected net after the stated
            player deltas,” not the league’s historical <code className="font-mono text-xs">NET_RATING</code> for the
            original five.
          </li>
        </ul>
      </div>

      {/* ——— Technical ——— */}
      <section id="data-and-scope" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Data and season scope</h2>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Season:</strong> <code className="text-xs font-mono">2025-26</code>,{' '}
            <strong className="text-slate-700 dark:text-slate-300">NBA regular season only</strong> (no playoffs, play-in,
            preseason, or All-Star) in all <code className="text-xs font-mono">nba_api</code> pulls.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Primary path:</strong> live ingestion from NBA Stats
            into SQLite when you run <code className="text-xs font-mono">python -m data_pipeline.ingest_all</code>. The UI
            exposes <code className="text-xs font-mono">GET /api/scope</code> so you can confirm the stored source (e.g.{' '}
            <code className="text-xs font-mono">nba_stats_api</code>).
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Optional demo:</strong>{' '}
            <code className="text-xs font-mono">python -m data_pipeline.ingest_all --seed</code> loads synthetic lineups
            for offline UI work only—not real minutes or real five-man combinations.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Storage:</strong> SQLite today; schema is written to
            be portable toward PostgreSQL if you outgrow a single file.
          </li>
        </ul>
      </section>

      <section id="pace-and-tempo" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Pace, possessions, and efficiency columns</h2>
        <p>
          The app ingests NBA.com advanced summaries. In the tables you will see <strong className="text-slate-800 dark:text-slate-200">efficiency</strong>, <strong className="text-slate-800 dark:text-slate-200">volume</strong>, and{' '}
          <strong className="text-slate-800 dark:text-slate-200">tempo</strong> on different scales—mixing them up is a
          common source of confusion.
        </p>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Offensive rating (ORtg) &amp; defensive rating (DRtg):</strong>{' '}
            For teams and five-man lineups in this build, these come from the league feed configured for{' '}
            <strong className="text-slate-800 dark:text-slate-200">per-100-possession</strong> reporting—i.e. expected
            points scored (ORtg) or allowed (DRtg) <em>per 100 possessions</em> for that row. They answer “how efficient
            per possession,” not “how many points per game.”
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Net rating (tables):</strong> The{' '}
            <strong className="text-slate-800 dark:text-slate-200">NET_RATING</strong> value from the same NBA.com lineup
            (or team) row—<strong className="text-slate-800 dark:text-slate-200">ingested directly</strong>, not recomputed
            by this app for live data. It is on the same per-100 scale as ORtg/DRtg and is conceptually “offensive minus
            defensive efficiency” for that unit; the UI shows the league’s number, not a custom replacement.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Pace:</strong> The <strong className="text-slate-800 dark:text-slate-200">Pace</strong> field on a <strong>team</strong> or <strong>lineup</strong> row is the league’s <strong className="text-slate-800 dark:text-slate-200">tempo</strong> statistic for that entity: in standard NBA.com presentation it reads as an estimate of{' '}
            <strong className="text-slate-800 dark:text-slate-200">possessions per 48 minutes</strong> (full regulation
            length). <strong>Higher pace ⇒ more possessions per 48</strong> for that unit’s time on the floor. It does{' '}
            <em>not</em> measure shot-making quality by itself—pair pace with ORtg/DRtg/Net and with minutes to interpret
            small samples.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Possessions column (lineups):</strong> When the API
            provides lineup possessions we store them; otherwise the pipeline may approximate from minutes and pace-style
            signals for downstream use (e.g. ULS). Check raw minutes alongside any derived possession estimate.
          </li>
        </ul>
      </section>

      <section id="minute-floors" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Minute floors (what each screen asks for)</h2>
        <p>
          There is <strong className="text-slate-800 dark:text-slate-200">no single global cutoff</strong>. Each view
          requests lineups with at least <strong>X</strong> minutes played <em>together</em>; <strong>X</strong> differs by
          page and URL parameters.
        </p>
        <ul className="list-disc pl-5 space-y-2 marker:text-court-accent">
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Leaderboard</strong> defaults to{' '}
            <strong>50</strong> minutes (slider can change it), aligned with ULS eligibility so the table usually shows
            scores instead of blanks. The API default for generic lineup lists matches that product choice when{' '}
            <code className="font-mono text-xs">min_minutes</code> is omitted.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Home</strong> uses high floors (often 80–100) for
            featured samples so cards are not dominated by tiny-sample noise.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Team explorer</strong> uses different floors per
            column: e.g. <strong>50</strong> for “best net,” <strong>40</strong> for the ORtg–DRtg scatter sample,{' '}
            <strong>0</strong> for “most minutes,” and <strong>50</strong> for “most underrated (ULS)” so every row in
            that slice has a computed ULS (same threshold as the score itself).
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Substitution simulator</strong> uses{' '}
            <strong>30</strong> minutes minimum for lineup choices (so the dropdown still has options without ultra-rare
            groups), and loads up to <strong>100</strong> of that team’s heaviest-minute lineups for the menu.
          </li>
          <li>
            <strong className="text-slate-700 dark:text-slate-300">Underrated (ULS) page</strong> defaults to{' '}
            <strong>50</strong> minutes for the list; the slider cannot go below 50 because{' '}
            <strong>ULS is undefined below that floor</strong> (see ULS section).
          </li>
        </ul>
      </section>

      <section id="lineup-traits" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Lineup fit traits (spacing, playmaking, defense, rebounding)</h2>
        <p>
          These are <strong className="text-slate-800 dark:text-slate-200">descriptive</strong> scores built from the five
          roster players attached to a lineup row: shooting mix, assist and turnover signals, steal/block activity and
          DBPM (Defensive Box Plus/Minus) proxies, and rebound volume. Each raw trait column is computed for every lineup, then{' '}
          <strong className="text-slate-800 dark:text-slate-200">winsorized at the 2nd and 98th percentiles</strong> and
          scaled to <strong>0–100 with min–max</strong> across the league lineup population in the database at enrichment
          time.
        </p>
        <p>
          Traits <strong className="text-slate-800 dark:text-slate-200">do not drive ULS</strong> and are not winsorized
          inside the ULS formula—they help you <em>describe</em> a unit next to efficiency numbers, not replace them.
        </p>
      </section>

      <section id="uls-formula" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Underrated Lineup Score (ULS)—explicit definition</h2>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">Eligibility.</strong> Only lineups with{' '}
          <strong>minutes ≥ 50</strong> enter the ULS calculation. Everyone else gets a missing ULS (shown as “—” in the
          UI).
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">Normalization <code className="font-mono text-xs">norm(x)</code>.</strong>{' '}
          For each ingredient below, take all <em>eligible</em> lineups (minutes ≥ 50), collect that ingredient’s values,
          and apply <strong>pure min–max to 0–100</strong> on that set:{' '}
          <code className="font-mono text-xs">100 × (x − min) / (max − min)</code>. There is{' '}
          <strong>no winsorization inside ULS</strong>. If <code className="font-mono text-xs">max == min</code> for an
          ingredient, every lineup receives <strong>50</strong> for that ingredient (avoids divide-by-zero).
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">Defensive rating (lower is better).</strong> Before
          normalizing, defensive rating is <strong>negated</strong> so that better defense (lower DRtg) maps to a higher
          value after scaling: use <code className="font-mono text-xs">−defensive_rating</code> inside{' '}
          <code className="font-mono text-xs">norm</code>.
        </p>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">Limited Usage Bonus (LUB)—two steps.</strong> Among
          eligible minutes (≥ 50) only:
        </p>
        <ol className="list-decimal pl-5 space-y-2 marker:text-court-accent">
          <li>
            Raw bonus:{' '}
            <code className="font-mono text-xs text-slate-300">
              LUB_raw = 1 − (minutes − min(minutes)) / (max(minutes) − min(minutes))
            </code>
            . Fewer minutes together ⇒ higher <code className="font-mono text-xs">LUB_raw</code>. If all eligible
            lineups share the same minute total, <code className="font-mono text-xs">LUB_raw = 1</code> for all.
          </li>
          <li>
            Then <strong>normalize again</strong>: <code className="font-mono text-xs">norm(LUB_raw)</code> to 0–100
            across the same eligible set—so the “usage” axis is comparable to the other ingredients.
          </li>
        </ol>
        <p>
          <strong className="text-slate-800 dark:text-slate-200">Possessions.</strong> If a lineup row lacks
          possessions, the pipeline uses <code className="font-mono text-xs">minutes × 2</code> as a fallback before{' '}
          <code className="font-mono text-xs">norm</code>.
        </p>
        <p className="text-slate-700 dark:text-slate-300">
          <strong className="text-court-950 dark:text-white">Final ULS</strong> is the weighted sum of the five normalized
          ingredients (weights sum to 1):
        </p>
        <CodeBlock>{`ULS =
    0.35 × norm(net_rating)
  + 0.20 × norm(offensive_rating)
  + 0.20 × norm(−defensive_rating)
  + 0.15 × norm(LUB_raw)     ← LUB_raw from the two-step LUB above; this is the second min–max
  + 0.10 × norm(possessions)`}</CodeBlock>
        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <p className="font-medium text-slate-700 dark:text-slate-300">What each weight is doing</p>
          <p>
            Weights are a <strong className="text-slate-700 dark:text-slate-300">fixed product spec</strong> (they sum to{' '}
            <strong className="text-slate-700 dark:text-slate-300">1.0</strong>) applied <em>after</em> each ingredient is
            scaled to 0–100 on the eligible lineup set. They are not re-fit from data inside the app.
          </p>
          <ul className="list-disc pl-5 space-y-1.5 marker:text-court-accent">
            <li>
              <strong className="text-slate-700 dark:text-slate-300">0.35 on net rating</strong> — largest slice: overall
              per-possession margin (ORtg − DRtg on the row) is the single best summary of how good the unit was, so it
              anchors the score.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">0.20 on offensive rating</strong> — keeps{' '}
              <em>offensive efficiency</em> visible on its own, not only through net (e.g. elite offense dragged by defense
              in a small sample still registers).
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">0.20 on inverted defensive rating</strong> — same-sized
              slice for <em>defensive efficiency</em>, after negating DRtg so lower allowed (better defense) scores higher
              once normalized.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">0.15 on LUB</strong> — the “underrated” axis among
              lineups that already cleared the minutes gate: fewer shared minutes within the qualified pool nudges the
              composite up versus peers with similar efficiency on heavier run.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">0.10 on possessions</strong> — a modest volume
              tiebreaker so all else equal, lineups with more documented opportunity can separate from extreme low-minute
              outliers; small enough that the score does not become “who plays the most.”
            </li>
          </ul>
        </div>
      </section>

      <section id="substitution-simulator" className="space-y-4 scroll-mt-24">
        <h2 className="text-xl font-display text-court-950 dark:text-white">Substitution simulator—explicit definition</h2>
        <p className="rounded-lg border border-court-accent/30 bg-court-accent/10 px-4 py-3 text-slate-800 dark:text-slate-200 text-sm">
          <strong className="text-court-950 dark:text-white">Important:</strong> Everything in this section is{' '}
          <strong>only</strong> for the simulator output. The <strong>Net</strong> (and ORtg/DRtg) you see in lineup
          tables elsewhere still come from <strong>NBA Stats ingestion</strong> until you run a simulation—then the API
          returns <em>additional</em> projected fields alongside those baselines. See also{' '}
          <a href="#league-vs-app-metrics" className="text-court-accent font-medium hover:underline">
            League numbers vs app-only calculations
          </a>
          .
        </p>
        <p>
          Start from the <strong className="text-slate-800 dark:text-slate-200">observed lineup</strong> offensive and
          defensive ratings (<code className="font-mono text-xs">CurrentOff</code>, <code className="font-mono text-xs">CurrentDef</code>
          )—those baselines are the <strong className="text-slate-800 dark:text-slate-200">same NBA-sourced ORtg/DRtg</strong>{' '}
          already stored for that lineup. Then apply <strong className="text-slate-800 dark:text-slate-200">this app’s</strong>{' '}
          player-in vs player-out deltas on OBPM (Offensive Box Plus/Minus), TS% (True Shooting Percentage), AST%
          (Assist Percentage), TOV% (Turnover Percentage), DBPM (Defensive Box Plus/Minus), STL% (Steal Percentage), and
          BLK% (Block Percentage). Percent stats must be{' '}
          <strong className="text-slate-800 dark:text-slate-200">decimals</strong> (e.g. true shooting{' '}
          <code className="font-mono text-xs">0.58</code>, not <code className="font-mono text-xs">58</code>).
        </p>
        <p className="text-slate-700 dark:text-slate-300">
          <strong className="text-court-950 dark:text-white">Projected offensive rating</strong>
        </p>
        <CodeBlock>{`ProjOff = CurrentOff
        + 1.8 × (OBPM_in − OBPM_out)
        + 8.0 × (TS_in − TS_out)
        + 0.12 × (ASTpct_in − ASTpct_out)
        − 0.08 × (TOVpct_in − TOVpct_out)`}</CodeBlock>
        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <p className="font-medium text-slate-700 dark:text-slate-300">Coefficients on projected offense</p>
          <p>
            These are <strong className="text-slate-700 dark:text-slate-300">linear sensitivities</strong> in{' '}
            <strong className="text-slate-700 dark:text-slate-300">points per 100 possessions</strong> on the lineup’s
            projected ORtg for each one-unit change in the player swap (they do <em>not</em> sum to 1 like ULS weights).
            Percent stats are <strong className="text-slate-700 dark:text-slate-300">decimals</strong> (e.g. 0.58 TS%).
          </p>
          <ul className="list-disc pl-5 space-y-1.5 marker:text-court-accent">
            <li>
              <strong className="text-slate-700 dark:text-slate-300">+1.8 × ΔOBPM</strong> — OBPM is on a BPM-style
              scale; each full point of OBPM edge for the incoming player lifts projected ORtg by about 1.8 per 100 at the
              margin.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">+8.0 × ΔTS</strong> — true shooting moves in tiny
              decimals, so the coefficient is large: a +0.01 TS edge (one percentage point expressed as 0.01) shifts
              projected ORtg by about <strong className="text-slate-700 dark:text-slate-300">+0.08</strong> per 100 through
              this term alone.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">+0.12 × ΔAST%</strong> — assist percentage as a
              decimal; a +0.05 gap (five percentage points as 0.05) adds about{' '}
              <strong className="text-slate-700 dark:text-slate-300">+0.006</strong> ORtg per 100 through this channel.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">−0.08 × ΔTOV%</strong> — turnover percentage as a
              decimal; the leading minus means a higher incoming TOV% <em>hurts</em> projected offense (more dead
              possessions).
            </li>
          </ul>
        </div>
        <p className="text-slate-700 dark:text-slate-300">
          <strong className="text-court-950 dark:text-white">Projected defensive rating</strong> (lower allowed is better)
        </p>
        <CodeBlock>{`ProjDef = CurrentDef
        − 1.5 × (DBPM_in − DBPM_out)
        − 0.10 × (STLpct_in − STLpct_out)
        − 0.10 × (BLKpct_in − BLKpct_out)`}</CodeBlock>
        <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
          <p className="font-medium text-slate-700 dark:text-slate-300">Coefficients on projected defense</p>
          <p>
            <code className="font-mono text-xs">CurrentDef</code> is points allowed per 100 (lower is better). Each term
            below <strong className="text-slate-700 dark:text-slate-300">subtracts</strong> from{' '}
            <code className="font-mono text-xs">CurrentDef</code>, so a positive swap delta in a “good” defensive signal
            lowers projected points allowed.
          </p>
          <ul className="list-disc pl-5 space-y-1.5 marker:text-court-accent">
            <li>
              <strong className="text-slate-700 dark:text-slate-300">−1.5 × ΔDBPM</strong> — DBPM on a BPM-style scale;
              about 1.5 points per 100 allowed shaved off for each full point of DBPM improvement in the swap.
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">−0.10 × ΔSTL%</strong> — steal rate as a decimal
              (e.g. 0.02); a +0.01 gap moves this layer by 0.10 × 0.01 ={' '}
              <strong className="text-slate-700 dark:text-slate-300">0.001</strong> on the projected allowed scale (small
              next to DBPM, but directionally rewards higher steal activity).
            </li>
            <li>
              <strong className="text-slate-700 dark:text-slate-300">−0.10 × ΔBLK%</strong> — block rate as a decimal,
              same multiplier as steals: a +0.01 gap contributes 0.001 through this term alone; DBPM still carries most
              of the defensive shift in typical swaps.
            </li>
          </ul>
        </div>
        <p className="text-slate-700 dark:text-slate-300">
          <strong className="text-court-950 dark:text-white">Projected net rating</strong>
        </p>
        <CodeBlock>{`ProjNet = ProjOff − ProjDef`}</CodeBlock>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          <strong className="text-slate-700 dark:text-slate-300">No extra weights here:</strong>{' '}
          <code className="font-mono text-xs">ProjNet</code> is simply the spread between the two projected per-100 ratings
          above—the same ORtg − DRtg idea applied to <em>projected</em> offense and defense, not another weighted blend.
        </p>
        <p>
          <code className="font-mono text-xs">ProjNet</code> is <strong className="text-slate-800 dark:text-slate-200">not</strong> a
          relabeled copy of the league’s lineup <code className="font-mono text-xs">NET_RATING</code>. It is the difference
          between two <em>projected</em> per-100-style ratings produced only by the formulas above. The historical{' '}
          <strong>Net</strong> column in the rest of the app is unchanged by this calculation.
        </p>
        <p>
          There is <strong className="text-slate-800 dark:text-slate-200">no shrink toward team ratings</strong> in this
          build—the projection is entirely the lineup baseline plus the stated deltas.
        </p>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">What’s in the product (routes)</h2>
        <dl className="space-y-3 text-sm">
          <div>
            <dt className="font-mono text-court-line uppercase text-xs">Leaderboard</dt>
            <dd>League-wide lineup table: sort, search, minute floors, CSV export.</dd>
          </div>
          <div>
            <dt className="font-mono text-court-line uppercase text-xs">Team explorer</dt>
            <dd>Within-team contrasts: high net vs heavy minutes vs ULS-ranked samples.</dd>
          </div>
          <div>
            <dt className="font-mono text-court-line uppercase text-xs">Underrated</dt>
            <dd>Sortable ULS view: minutes floor is <strong>≥ 50</strong> (same as ULS computation—scores are blank below that).</dd>
          </div>
          <div>
            <dt className="font-mono text-court-line uppercase text-xs">Substitution simulator</dt>
            <dd>Swap one roster player into a selected observed lineup; see projected ORtg/DRtg/net and narrative summary.</dd>
          </div>
        </dl>
      </section>

      <section className="rounded-xl border-2 border-amber-500/40 bg-amber-950/20 dark:bg-amber-950/30 px-5 py-5 space-y-3 scroll-mt-24">
        <h2 className="text-xl font-display text-amber-100 dark:text-amber-50">Limitations (read this)</h2>
        <p className="text-amber-100/95 dark:text-amber-100/90">
          Building trust means stating what the app <strong>does not</strong> know. Treat every insight as conditional on
          these constraints:
        </p>
        <ul className="list-disc pl-5 space-y-2 text-amber-100/90 dark:text-amber-100/85 marker:text-amber-400">
          <li>
            <strong className="text-amber-50">Context dependence:</strong> opponent strength, home/road, garbage time, and
            game script are not layered into the public lineup tables this build consumes.
          </li>
          <li>
            <strong className="text-amber-50">No player tracking:</strong> no second-spectrum spacing pressure, close-out
            speed, or pick-and-roll coverage tags—only what box-style and advanced summaries approximate.
          </li>
          <li>
            <strong className="text-amber-50">No scheme labels:</strong> the app does not classify “switch everything” vs
            “drop” vs “ice”; defensive rating is an outcome, not a playbook.
          </li>
          <li>
            <strong className="text-amber-50">No injury or availability modeling:</strong> substitutions are statistical
            thought experiments, not workload or medical recommendations.
          </li>
          <li>
            <strong className="text-amber-50">Survivorship and selection:</strong> coaches pick who plays together;
            observed lineups reflect those choices, not random assignment.
          </li>
          <li>
            <strong className="text-amber-50">Public data caps:</strong> ingestion may not return every theoretical five-man
            combination league-wide—only what the upstream feed exposes for the configured season and season type.
          </li>
          <li>
            <strong className="text-amber-50">Player proxies:</strong> when true BPM is unavailable from the feed, OBPM
            (Offensive Box Plus/Minus) and DBPM (Defensive Box Plus/Minus) may be proxied from offensive/defensive rating
            vs league quantiles during ingestion—noisy, but documented as a transparency tradeoff.
          </li>
        </ul>
      </section>

      <section className="space-y-4">
        <h2 className="text-xl font-display text-court-950 dark:text-white scroll-mt-24">Future directions</h2>
        <p>
          A natural roadmap—especially with richer data—includes matchup-aware projections, possession-level weighting
          (clutch vs garbage), defensive coverage or ball-screen taxonomy, transition frequency modeling,
          opponent-specific lineup recommendations, and eventually player-tracking integration. A dedicated case-study
          write-up (one team’s rotation efficiency vs usage, tied to film) would further bridge engineering and
          storytelling.
        </p>
      </section>

    </article>
  )
}
