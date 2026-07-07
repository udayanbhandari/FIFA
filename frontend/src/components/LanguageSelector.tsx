import React from "react";
import { Language } from "../lib/types";

interface Props {
  value: Language;
  onChange: (lang: Language) => void;
}

const LANGUAGES: Record<Language, string> = {
  en: "English (EN)",
  es: "Español (ES)",
  fr: "Français (FR)",
  ar: "العربية (AR)",
  pt: "Português (PT)",
  de: "Deutsch (DE)",
  ja: "日本語 (JA)",
  ko: "한국어 (KO)",
  zh: "中文 (ZH)",
};

export const LanguageSelector: React.FC<Props> = ({ value, onChange }) => {
  return (
    <div className="form-group" style={{ marginBottom: 0 }}>
      <label htmlFor="language-select" className="visually-hidden">
        Select Language
      </label>
      <select
        id="language-select"
        value={value}
        onChange={(e) => onChange(e.target.value as Language)}
        style={{ width: "auto", padding: "6px 12px", minWidth: "120px" }}
      >
        {Object.entries(LANGUAGES).map(([code, label]) => (
          <option key={code} value={code}>
            {label}
          </option>
        ))}
      </select>
    </div>
  );
};
