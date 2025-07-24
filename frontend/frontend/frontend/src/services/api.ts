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

  // Generic HTTP methods
  async get<T = any>(url: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error: any) {
      throw new Error(error.message || 'Network error');
    }
  }

  async post<T = any>(url: string, data?: any): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error: any) {
      throw new Error(error.message || 'Network error');
    }
  }

  async put<T = any>(url: string, data?: any): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: data ? JSON.stringify(data) : undefined
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error: any) {
      throw new Error(error.message || 'Network error');
    }
  }

  async delete<T = any>(url: string): Promise<T> {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'DELETE',
        headers: this.getHeaders()
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error: any) {
      throw new Error(error.message || 'Network error');
    }
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
        text: question.text || question.question_text,
        question_type: question.question_type,
        is_required: question.is_required,
        order_index: question.order_index,
        options: question.options,
        validation_rules: question.validation_rules || {},
        questionnaire_id: questionnaireId
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
        text: question.text || question.question_text,
        question_type: question.question_type,
        is_required: question.is_required,
        order_index: question.order_index,
        options: question.options,
        validation_rules: question.validation_rules || {},
        questionnaire_id: question.questionnaire_id
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

  // Real questionnaire methods using actual API endpoints
  async getQuestionnaires(): Promise<ApiResponse<any[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/questionnaires`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async saveQuestionnaire(questionnaire: any): Promise<ApiResponse<any>> {
    try {
      if (questionnaire.id) {
        // Update existing questionnaire
        const response = await fetch(`${API_BASE_URL}/questions/questionnaires/${questionnaire.id}`, {
          method: 'PUT',
          headers: this.getHeaders(),
          body: JSON.stringify({
            name: questionnaire.title,
            description: questionnaire.description,
            is_active: true
          })
        });
        return this.handleResponse(response);
      } else {
        return { error: 'Cannot save questionnaire without ID' };
      }
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getQuestionnaire(id: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/questions/questionnaires/${id}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
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

  // AI Guidelines methods
  async generateAiGuidelines(programId: number, model?: string): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/generate?program_id=${programId}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ model: model || "anthropic/claude-3.5-sonnet" })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getActiveGuidelines(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/active?program_id=${programId}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getGuidelinesHistory(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/history?program_id=${programId}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async saveAiGuidelines(programId: number, guidelines: any, isActive: boolean = false, notes?: string): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/save?program_id=${programId}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ guidelines, is_active: isActive, notes })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async activateGuidelinesVersion(programId: number, version: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/activate?program_id=${programId}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ version })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async getGuidelinesStatus(programId: number): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/status?program_id=${programId}`, {
        method: 'GET',
        headers: this.getHeaders()
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }

  async generateAndSaveGuidelines(programId: number, model?: string, activateImmediately: boolean = false, notes?: string): Promise<ApiResponse<any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/ai-guidelines/generate-and-save?program_id=${programId}`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ 
          model: model || "anthropic/claude-3.5-sonnet", 
          activate_immediately: activateImmediately,
          notes 
        })
      });
      return this.handleResponse(response);
    } catch (error) {
      return { error: 'Network error' };
    }
  }
}

export const apiService = new ApiService();
export default apiService;