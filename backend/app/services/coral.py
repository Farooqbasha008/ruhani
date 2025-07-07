import os
import httpx
import json
import uuid
import base64
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union

CORAL_API_KEY = os.getenv("CORAL_API_KEY")
CORAL_API_BASE_URL = os.getenv("CORAL_API_BASE_URL", "https://api.coralprotocol.com/v1")

class CoralClient:
    """Client for Coral Protocol - a decentralized identity and verifiable credential protocol.
    
    This client provides functionality for:
    1. Managing decentralized identifiers (DIDs) for employees
    2. Issuing verifiable credentials for wellness sessions
    3. Managing consent and permissioned access to data
    4. Ensuring privacy compliance through credential-based access control
    """
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {CORAL_API_KEY}",
            "Content-Type": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def create_did(self, employee_id: str, name: str, email: str) -> Dict[str, Any]:
        """Create a decentralized identifier (DID) for an employee.
        
        Args:
            employee_id: Unique identifier for the employee
            name: Employee's name
            email: Employee's email address
            
        Returns:
            Dictionary containing the DID information
        """
        if not CORAL_API_KEY:
            # In development, we'll create a mock DID
            did = f"did:coral:{hashlib.sha256(employee_id.encode()).hexdigest()[:16]}"
            did_document = {
                "@context": "https://www.w3.org/ns/did/v1",
                "id": did,
                "created": datetime.utcnow().isoformat(),
                "authentication": [{
                    "id": f"{did}#keys-1",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                    "publicKeyMultibase": f"z{base64.b64encode(uuid.uuid4().bytes).decode()}"
                }]
            }
            return {
                "did": did,
                "did_document": did_document,
                "mock": True
            }
        
        url = f"{CORAL_API_BASE_URL}/did/create"
        payload = {
            "employee_id": employee_id,
            "name": name,
            "email": email
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error creating DID with Coral: {str(e)}")
            return {"error": f"Error creating DID with Coral: {str(e)}"}
    
    async def resolve_did(self, did: str) -> Dict[str, Any]:
        """Resolve a DID to get its DID document.
        
        Args:
            did: The decentralized identifier to resolve
            
        Returns:
            Dictionary containing the DID document
        """
        if not CORAL_API_KEY:
            # In development, we'll create a mock DID document
            did_document = {
                "@context": "https://www.w3.org/ns/did/v1",
                "id": did,
                "created": datetime.utcnow().isoformat(),
                "authentication": [{
                    "id": f"{did}#keys-1",
                    "type": "Ed25519VerificationKey2020",
                    "controller": did,
                    "publicKeyMultibase": f"z{base64.b64encode(uuid.uuid4().bytes).decode()}"
                }]
            }
            return {"did_document": did_document, "mock": True}
        
        url = f"{CORAL_API_BASE_URL}/did/resolve/{did}"
        
        try:
            response = await self.client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error resolving DID with Coral: {str(e)}")
            return {"error": f"Error resolving DID with Coral: {str(e)}"}
    
    async def issue_credential(self, 
                             issuer_did: str, 
                             subject_did: str, 
                             credential_type: str,
                             claims: Dict[str, Any],
                             expiration_days: int = 365) -> Dict[str, Any]:
        """Issue a verifiable credential.
        
        Args:
            issuer_did: DID of the credential issuer (typically the organization)
            subject_did: DID of the credential subject (typically an employee)
            credential_type: Type of credential (e.g., 'WellnessSession', 'ConsentGrant')
            claims: Dictionary of claims to include in the credential
            expiration_days: Number of days until the credential expires
            
        Returns:
            Dictionary containing the verifiable credential
        """
        if not CORAL_API_KEY:
            # In development, we'll create a mock credential
            credential_id = str(uuid.uuid4())
            issuance_date = datetime.utcnow().isoformat()
            expiration_date = (datetime.utcnow() + timedelta(days=expiration_days)).isoformat()
            
            credential = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/examples/v1"
                ],
                "id": f"urn:uuid:{credential_id}",
                "type": ["VerifiableCredential", credential_type],
                "issuer": issuer_did,
                "issuanceDate": issuance_date,
                "expirationDate": expiration_date,
                "credentialSubject": {
                    "id": subject_did,
                    **claims
                },
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": issuance_date,
                    "verificationMethod": f"{issuer_did}#keys-1",
                    "proofPurpose": "assertionMethod",
                    "proofValue": f"z{base64.b64encode(uuid.uuid4().bytes).decode()}"
                }
            }
            
            return {"credential": credential, "mock": True}
        
        url = f"{CORAL_API_BASE_URL}/credentials/issue"
        payload = {
            "issuer_did": issuer_did,
            "subject_did": subject_did,
            "credential_type": credential_type,
            "claims": claims,
            "expiration_days": expiration_days
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error issuing credential with Coral: {str(e)}")
            return {"error": f"Error issuing credential with Coral: {str(e)}"}
    
    async def verify_credential(self, credential: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a credential's authenticity and validity.
        
        Args:
            credential: The verifiable credential to verify
            
        Returns:
            Dictionary containing verification results
        """
        if not CORAL_API_KEY:
            # In development, we'll mock verification
            return {
                "verified": True,
                "expired": False,
                "revoked": False,
                "mock": True
            }
        
        url = f"{CORAL_API_BASE_URL}/credentials/verify"
        payload = {"credential": credential}
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error verifying credential with Coral: {str(e)}")
            return {"error": f"Error verifying credential with Coral: {str(e)}"}
    
    async def create_presentation(self, 
                                credentials: List[Dict[str, Any]], 
                                holder_did: str,
                                audience: str) -> Dict[str, Any]:
        """Create a verifiable presentation from one or more credentials.
        
        Args:
            credentials: List of verifiable credentials to include
            holder_did: DID of the presentation holder
            audience: Intended recipient of the presentation
            
        Returns:
            Dictionary containing the verifiable presentation
        """
        if not CORAL_API_KEY:
            # In development, we'll create a mock presentation
            presentation_id = str(uuid.uuid4())
            creation_date = datetime.utcnow().isoformat()
            
            presentation = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1"
                ],
                "id": f"urn:uuid:{presentation_id}",
                "type": ["VerifiablePresentation"],
                "holder": holder_did,
                "verifiableCredential": credentials,
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": creation_date,
                    "verificationMethod": f"{holder_did}#keys-1",
                    "proofPurpose": "authentication",
                    "challenge": str(uuid.uuid4()),
                    "domain": audience,
                    "proofValue": f"z{base64.b64encode(uuid.uuid4().bytes).decode()}"
                }
            }
            
            return {"presentation": presentation, "mock": True}
        
        url = f"{CORAL_API_BASE_URL}/presentations/create"
        payload = {
            "credentials": credentials,
            "holder_did": holder_did,
            "audience": audience
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error creating presentation with Coral: {str(e)}")
            return {"error": f"Error creating presentation with Coral: {str(e)}"}
    
    async def verify_presentation(self, presentation: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a presentation's authenticity and validity.
        
        Args:
            presentation: The verifiable presentation to verify
            
        Returns:
            Dictionary containing verification results
        """
        if not CORAL_API_KEY:
            # In development, we'll mock verification
            return {
                "verified": True,
                "credentials_verified": True,
                "mock": True
            }
        
        url = f"{CORAL_API_BASE_URL}/presentations/verify"
        payload = {"presentation": presentation}
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error verifying presentation with Coral: {str(e)}")
            return {"error": f"Error verifying presentation with Coral: {str(e)}"}
    
    async def revoke_credential(self, credential_id: str, issuer_did: str) -> Dict[str, Any]:
        """Revoke a previously issued credential.
        
        Args:
            credential_id: ID of the credential to revoke
            issuer_did: DID of the credential issuer
            
        Returns:
            Dictionary containing revocation status
        """
        if not CORAL_API_KEY:
            # In development, we'll mock revocation
            return {
                "revoked": True,
                "revocation_date": datetime.utcnow().isoformat(),
                "mock": True
            }
        
        url = f"{CORAL_API_BASE_URL}/credentials/revoke"
        payload = {
            "credential_id": credential_id,
            "issuer_did": issuer_did
        }
        
        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Coral API error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error: {e.response.status_code}", "details": e.response.text}
        except Exception as e:
            print(f"Error revoking credential with Coral: {str(e)}")
            return {"error": f"Error revoking credential with Coral: {str(e)}"}
    
    async def create_consent_credential(self, 
                                      issuer_did: str, 
                                      subject_did: str,
                                      data_categories: List[str],
                                      authorized_parties: List[str],
                                      purpose: str,
                                      expiration_days: int = 90) -> Dict[str, Any]:
        """Create a consent credential that grants access to specific data categories.
        
        Args:
            issuer_did: DID of the consent issuer (typically the employee)
            subject_did: DID of the consent subject (typically the organization)
            data_categories: List of data categories consent is granted for
            authorized_parties: List of DIDs authorized to access the data
            purpose: Purpose for which consent is granted
            expiration_days: Number of days until consent expires
            
        Returns:
            Dictionary containing the consent credential
        """
        claims = {
            "consentFor": {
                "dataCategories": data_categories,
                "authorizedParties": authorized_parties,
                "purpose": purpose
            }
        }
        
        return await self.issue_credential(
            issuer_did=issuer_did,
            subject_did=subject_did,
            credential_type="ConsentCredential",
            claims=claims,
            expiration_days=expiration_days
        )
    
    async def create_session_credential(self,
                                      issuer_did: str,
                                      subject_did: str,
                                      session_id: str,
                                      session_date: str,
                                      mood: str,
                                      risk_level: str,
                                      summary_hash: str,
                                      expiration_days: int = 365) -> Dict[str, Any]:
        """Create a wellness session credential.
        
        Args:
            issuer_did: DID of the credential issuer (typically the organization)
            subject_did: DID of the credential subject (typically the employee)
            session_id: Unique identifier for the session
            session_date: Date of the session
            mood: Mood recorded during the session
            risk_level: Risk level assessed during the session
            summary_hash: Hash of the session summary (for privacy)
            expiration_days: Number of days until the credential expires
            
        Returns:
            Dictionary containing the session credential
        """
        claims = {
            "sessionDetails": {
                "sessionId": session_id,
                "sessionDate": session_date,
                "mood": mood,
                "riskLevel": risk_level,
                "summaryHash": summary_hash
            }
        }
        
        return await self.issue_credential(
            issuer_did=issuer_did,
            subject_did=subject_did,
            credential_type="WellnessSessionCredential",
            claims=claims,
            expiration_days=expiration_days
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()