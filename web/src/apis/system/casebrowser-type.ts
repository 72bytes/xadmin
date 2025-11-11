/**
 * Case Browser Type Definitions
 */

export interface CaseMetadata {
  casespace: string
  caseName: string
  tags: string[]
}

export interface CaseOption {
  key: string
  value: string
}

export interface CaseDetail extends CaseMetadata {
  options: CaseOption[]
}

export interface AddTagRequest {
  casespace: string
  caseName: string
  tag: string
}

export interface AddOptionRequest {
  casespace: string
  caseName: string
  key: string
  value: string
}

export interface UpdateOptionRequest {
  casespace: string
  caseName: string
  key: string
  value: string
}

