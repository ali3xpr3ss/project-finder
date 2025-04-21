import React, { useState, useEffect } from 'react';
import apiClient from '../axios';

function CreateProject({ onProjectCreated }: { onProjectCreated: () => void }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await apiClient.post('/v1/projects', { name, description });
      setMessage('Проект создан!');
      setName('');
      setDescription('');
      onProjectCreated();
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Ошибка создания проекта');
    }
  };

  return (
    <div>
      <h3>Создать проект</h3>
      <form onSubmit={handleSubmit}>
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
    </div>
  );
}

export default CreateProject;
