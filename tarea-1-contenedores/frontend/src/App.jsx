import { useEffect, useState } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:3000'

const STATUSES = ['pending', 'in_progress', 'done']

export default function App() {
  const [tasks, setTasks] = useState([])
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('') // coma-separadas, ej: dev,python
  const [statusFilter, setStatusFilter] = useState('')
  const [tagFilter, setTagFilter] = useState('')

  async function fetchTasks() {
    const params = new URLSearchParams()
    if (statusFilter) params.append('status', statusFilter)
    if (tagFilter) params.append('tag', tagFilter)
    const res = await fetch(`${API}/api/tasks?${params.toString()}`)
    const data = await res.json()
    setTasks(data)
  }

  useEffect(() => {
    fetchTasks().catch(console.error)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [statusFilter, tagFilter])

  async function createTask(e) {
    e.preventDefault()
    const payload = {
      title,
      description: description || null,
      tags: tags ? tags.split(',').map(s => s.trim()).filter(Boolean) : [],
      status: 'pending'
    }
    await fetch(`${API}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    setTitle(''); setDescription(''); setTags('')
    await fetchTasks()
  }

  async function deleteTask(id) {
    await fetch(`${API}/api/tasks/${id}`, { method: 'DELETE' })
    await fetchTasks()
  }

  async function cycleStatus(t) {
    const idx = STATUSES.indexOf(t.status)
    const next = STATUSES[(idx + 1) % STATUSES.length]
    await fetch(`${API}/api/tasks/${t.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: next })
    })
    await fetchTasks()
  }

  return (
    <main style={{ maxWidth: 800, margin: '0 auto', padding: 24, fontFamily: 'system-ui' }}>
      <h1 style={{ marginBottom: 8 }}>To-Do con etiquetas</h1>

      {/* Filtros */}
      <section style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
        <label>
          Estado:{' '}
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="">(todos)</option>
            {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label>
          Etiqueta:{' '}
          <input
            placeholder="p.ej. dev"
            value={tagFilter}
            onChange={e => setTagFilter(e.target.value)}
            style={{ width: 140 }}
          />
        </label>
        <button onClick={fetchTasks}>Refrescar</button>
      </section>

      {/* Formulario crear */}
      <form onSubmit={createTask} style={{ display: 'grid', gap: 8, marginBottom: 24 }}>
        <input
          required
          placeholder="Título"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />
        <textarea
          placeholder="Descripción (opcional)"
          value={description}
          onChange={e => setDescription(e.target.value)}
        />
        <input
          placeholder="Etiquetas separadas por coma (ej: dev, python)"
          value={tags}
          onChange={e => setTags(e.target.value)}
        />
        <button type="submit">Añadir tarea</button>
      </form>

      {/* Lista */}
      <ul style={{ listStyle: 'none', padding: 0, display: 'grid', gap: 12 }}>
        {tasks.map(t => (
          <li key={t.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>{t.title}</strong>
                <div style={{ fontSize: 13, color: '#555' }}>{t.description}</div>
                <div style={{ fontSize: 12, marginTop: 6 }}>
                  Estado: <code>{t.status}</code>{' '}
                  • Etiquetas: [{(t.tags || []).join(', ')}]
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button onClick={() => cycleStatus(t)}>Cambiar estado</button>
                <button onClick={() => deleteTask(t.id)} style={{ color: '#b00' }}>Borrar</button>
              </div>
            </div>
          </li>
        ))}
        {tasks.length === 0 && <li>No hay tareas aún.</li>}
      </ul>
    </main>
  )
}
