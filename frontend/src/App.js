import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';
import axios from 'axios';
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';
import { Select } from './components/ui/select';
import './index.css';

const categories = ["All", "Computer Science", "Data Science", "Mathematics", "Physics"];

const EventScholar = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const response = await axios.get('http://localhost:5000/events');
        setEvents(response.data);
      } catch (error) {
        console.error("Error fetching events data", error);
      }
    };
    fetchEvents();
  }, []);


  const filteredEvents = events.filter(event =>
    event.event_name && event.event_name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (selectedCategory === 'All' || event.topic === selectedCategory)
  );

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-center">Event Scholar</h1>
      
      <div className="mb-6 flex space-x-4">
        <div className="relative flex-grow">
          <Input
            type="text"
            placeholder="Search events..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 w-full"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
        </div>
        <Select
          value={selectedCategory}
          onValueChange={setSelectedCategory}
          className="w-48"
        >
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredEvents.map((event, index) => (
          <div key={index} className="bg-white shadow-md rounded-lg overflow-hidden">
            <div className="p-4">
              <h2 className="text-xl font-semibold mb-2">{event.event_name}</h2>
              <p className="text-sm text-gray-600 mb-2">{event.date} | {event.type}</p>
              <p className="text-sm text-gray-600 mb-2">{event.location}</p>
              <p className="text-sm mb-4">{event.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-blue-600">{event.topic}</span>
                {event.link && (
                  <a href={event.link} target="_blank" rel="noopener noreferrer">
                    <Button variant="outline">Learn More</Button>
                  </a>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EventScholar;
