import React, {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

function Report({title, rows}) {
  const max = Math.max(1, ...rows.map(row => row.count));
  return <section><h2>{title}</h2>{rows.length === 0 && <p>No listings yet.</p>}
    {rows.map(({label, count}) => <div key={label} className="row">
      <div className="label"><span>{label}</span><strong>{count}</strong></div>
      <div className="track"><div className="bar" style={{width: count / max * 100 + '%'}} /></div>
    </div>)}</section>;
}

function App() {
  const [reports, setReports] = useState(null);
  const [error, setError] = useState('');
  async function refresh() {
    setError('');
    try {
      const response = await fetch('/api/dashboard');
      if (!response.ok) throw Error();
      setReports(await response.json());
    } catch { setError('Could not load reports. Check that the API and database are running.'); }
  }
  useEffect(() => { refresh(); }, []);
  return <><header><small>DIRECTORY ANALYTICS</small><h1>Business listings</h1>
    <p>{reports ? reports.city.reduce((n,r) => n + r.count, 0) + ' listings in the database' : 'Loading reports…'}</p>
    <button onClick={refresh}>Refresh counts</button></header>{error && <p role="alert">{error}</p>}
    {reports && <article>{Object.entries({city:'By city', category:'By category', source:'By source'}).map(([key,title]) =>
      <Report key={key} title={title} rows={reports[key]} />)}</article>}</>;
}
createRoot(document.getElementById('root')).render(<App/>);
