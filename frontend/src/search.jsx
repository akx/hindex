import * as React from "react";
import * as ReactDOM from "react-dom";
import useSWR from "swr";
//
// function useLatest(value) {
//   const ref = React.useRef(value);
//   ref.current = value;
//   return ref;
// }

function getMatchingTerms(terms, search) {
  const matchingTerms = {};
  const requiredSubIds = new Set();
  if (search.length >= 2) {
    for (let term in terms) {
      const td = terms[term];
      const [subId, nd, nt, vars] = td;
      if (term.startsWith(search) || vars.some((v) => v.startsWith(search))) {
        matchingTerms[term] = td;
        requiredSubIds.add(subId);
      }
    }
  }
  return { matchingTerms, requiredSubIds };
}

function ResultView({ matchingTerms, subIndexes, docMap }) {
  return (
    <ul>
      {Object.keys(matchingTerms).map((termName) => {
        const termInfo = matchingTerms[termName];
        const [subId] = termInfo;
        const sub = subIndexes[subId];
        let details = null;
        if (sub && sub.data && sub.data.terms[termName]) {
          const occurrences = sub.data.terms[termName];
          details = (
            <ul>
              {occurrences.map((occ, i) => (
                <li key={i}>
                  <a href={docMap[occ.doc]}>
                    {occ.snippet.length ? (
                      <>
                        {occ.snippet[0]} <b>{occ.snippet[1]}</b>{" "}
                        {occ.snippet[2]}
                      </>
                    ) : (
                      JSON.stringify(occ)
                    )}
                  </a>
                </li>
              ))}
            </ul>
          );
        }
        return (
          <li key={termName}>
            {termName}
            {details}
          </li>
        );
      })}
    </ul>
  );
}

const App = () => {
  const [search, setSearch] = React.useState("");
  const [subIndexes, setSubIndexes] = React.useState({});
  const indexSWR = useSWR("./data/index.json");
  const { terms, docs } = indexSWR.data || {};
  const { matchingTerms, requiredSubIds } = React.useMemo(
    () => getMatchingTerms(terms, search),
    [terms, search]
  );
  React.useEffect(() => {
    if (!requiredSubIds.size) {
      return;
    }
    Array.from(requiredSubIds).forEach((subId) => {
      if (!subIndexes[subId]) {
        const promise = fetch(`data/${subId}.json`);
        const subObj = {
          promise,
          data: null,
        };
        promise.then(async (resp) => {
          subObj.data = await resp.json();
          setSubIndexes((s) => ({ ...s, [subId]: subObj }));
        });
        setSubIndexes((s) => ({ ...s, [subId]: subObj }));
      }
    });
  }, [subIndexes, requiredSubIds]);
  if (!indexSWR.data) {
    return <>Loading index...</>;
  }
  return (
    <div>
      <div>{Object.keys(terms).length} terms</div>
      <div>{Object.keys(docs).length} documents</div>
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search..."
      />
      {search ? (
        <ResultView
          matchingTerms={matchingTerms}
          subIndexes={subIndexes}
          docMap={docs}
        />
      ) : null}
    </div>
  );
};

ReactDOM.render(<App />, document.getElementById("root"));
