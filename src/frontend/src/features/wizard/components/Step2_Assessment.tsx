// المسار: src/app/components/wizard/Step2_Assessment.tsx
'use client';
import { useEffect, useState } from 'react';
import apiClient from '@/lib/api';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { AssessmentAnswer } from '@/app/wizard/page';

interface Question {
  id: string;
  skill: string;
  text: string;
  options: string[];
}
interface Props {
  jobRole: string;
  onComplete: (answers: AssessmentAnswer) => void;
}

export default function Step2_Assessment({ jobRole, onComplete }: Props) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [answers, setAnswers] = useState<AssessmentAnswer>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!jobRole) return;
    setIsLoading(true);
    apiClient.get<Question[]>(`/api/assessments/${encodeURIComponent(jobRole)}`)
      .then(res => setQuestions(res.data))
      .catch(err => console.error(err))
      .finally(() => setIsLoading(false));
  }, [jobRole]);
  
  const handleAnswerChange = (questionId: string, optionIndex: number) => {
    setAnswers(prev => ({ ...prev, [questionId]: optionIndex }));
  };

  if (isLoading) return <p>جارٍ تحميل الأسئلة...</p>;

  return (
    <div className="space-y-8">
      {questions.map((q) => (
        <div key={q.id}>
          <p className="font-semibold mb-4">{q.text}</p>
          <RadioGroup onValueChange={(value) => handleAnswerChange(q.id, parseInt(value))}>
            {q.options.map((option, index) => (
              <div key={index} className="flex items-center space-x-2">
                <RadioGroupItem value={index.toString()} id={`${q.id}-${index}`} />
                <Label htmlFor={`${q.id}-${index}`}>{option}</Label>
              </div>
            ))}
          </RadioGroup>
        </div>
      ))}
      <Button onClick={() => onComplete(answers)} disabled={Object.keys(answers).length !== questions.length}>
        التالي
      </Button>
    </div>
  );
}