const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiService {
  private getHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  private async handleResponse<T>(response: Response): Promise<ApiResponse<T>> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
      return { error: errorData.message || `HTTP ${response.status}` };
    }
    
    const data = await response.json();
    return { data };
  }

  // Question API methods
  async getQuestions(questionnaireId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/questionnaires/${questionnaireId}/questions`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async createQuestion(questionnaireId: number, question: any): Promise<ApiResponse<any>> {
    try {
      // Map frontend question format to backend format
      const backendQuestion = {
        text: question.question_text,
        question_type: question.question_type,
        is_required: question.is_required,
        order_index: question.order_index,
        options: question.options,
        validation_rules: question.validation_rules || {}
      };

      const response = await fetch(`${API_BASE_URL}/questions/questionnaires/${questionnaireId}/questions`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(backendQuestion)
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async updateQuestion(questionId: number, question: any): Promise<ApiResponse<any>> {
    try {
      const backendQuestion = {
        text: question.question_text,
        question_type: question.question_type,
        is_required: question.is_required,
        order_index: question.order_index,
        options: question.options,
        validation_rules: question.validation_rules || {}
      };

      const response = await fetch(`${API_BASE_URL}/questions/questions/${questionId}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(backendQuestion)
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async deleteQuestion(questionId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/questions/${questionId}`, {
        method: 'DELETE',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async reorderQuestions(questionnaireId: number, questionOrder: number[]): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/questionnaires/${questionnaireId}/questions/reorder`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ question_order: questionOrder })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  // Mock questionnaire methods (until backend endpoints are created)
  async getQuestionnaires(): Promise<ApiResponse<any[]>> {
    // TODO: Replace with actual API call when questionnaire endpoints are available
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          data: [
            {
              id: 1,
              title: "TechEd Accelerator 2024 Application",
              description: "Standard application form for our tech accelerator program",
              created_at: "2024-01-15T10:00:00Z",
              question_count: 0
            }
          ]
        });
      }, 500);
    });
  }

  async saveQuestionnaire(questionnaire: any): Promise<ApiResponse<any>> {
    // TODO: Replace with actual API call when questionnaire endpoints are available
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          data: {
            id: questionnaire.id || 1,
            title: questionnaire.title,
            description: questionnaire.description,
            created_at: new Date().toISOString()
          }
        });
      }, 1000);
    });
  }

  async getQuestionnaire(id: number): Promise<ApiResponse<any>> {
    // TODO: Replace with actual API call when questionnaire endpoints are available
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          data: {
            id: id,
            title: "TechEd Accelerator 2024 Application",
            description: "Standard application form for our tech accelerator program",
            questions: []
          }
        });
      }, 500);
    });
  }

  // Calibration API methods
  async getCalibrationQuestions(): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/questions`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getCalibrationStatus(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/status`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getCalibrationAnswers(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/answers`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getCalibrationSession(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/session`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async createCalibrationAnswer(programId: number, answer: any): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/answers`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(answer)
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async batchCreateCalibrationAnswers(programId: number, answers: any[]): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/answers/batch`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ answers })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getCalibrationAnswer(programId: number, questionKey: string): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/answers/${questionKey}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async deleteCalibrationAnswer(programId: number, questionKey: string): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/calibration/programs/${programId}/answers/${questionKey}`, {
        method: 'DELETE',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }
}

export const apiService = new ApiService();
export default apiService;