import React, { useState, useEffect } from 'react';
import apiClient from '../axios';

function Projects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');

  const fetchProjects = () => {
    setLoading(true);
    apiClient.get('/v1/projects')
      .then((response: any) => {
        setProjects(response.data);
        setLoading(false);
      })
      .catch((error: any) => {
        setMessage('Ошибка загрузки проектов');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await apiClient.post('/v1/projects', { name, description });
      setMessage('Проект создан!');
      setName('');
      setDescription('');
      fetchProjects();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Ошибка создания проекта');
    }
  };

  return (
    <div>
      <h2>Список проектов</h2>
      <form onSubmit={handleCreate}>
        <input
          type="text"
          placeholder="Название"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="text"
          placeholder="Описание"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <button type="submit">Создать</button>
      </form>
      {message && <p>{message}</p>}
      {loading ? (
        <p>Загрузка...</p>
      ) : projects.length > 0 ? (
        <ul>
          {projects.map((project) => (
            <li key={project.id}>{project.name} — {project.description}</li>
          ))}
        </ul>
      ) : (
        <p>Проекты не найдены.</p>
      )}
    </div>
  );
}

export default Projects;